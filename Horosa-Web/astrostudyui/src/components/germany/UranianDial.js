import { Component } from 'react';
import * as d3 from 'd3';
import { randomStr } from '../../utils/helper';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { projectToDial, cursorReadout, spreadDialAngles } from '../../utils/uranianDial';

const TAU = Math.PI * 2;
const norm360 = (x) => ((x % 360) + 360) % 360;
// 逆时针(0°在正上、度数向左增)，与全站星盘一致(AstroHelper.signsBand 用负角=逆时针)。
const polar = (cx, cy, R, deg) => { const a = deg / 360 * TAU; return [cx - R * Math.sin(a), cy - R * Math.cos(a)]; };

// 90°盘三 modality 扇区（各 30 黄道度 = 120 视觉度），柔色 + 代表星座字形。
// rep 用星座「名」字符串，配合 AstroChartFont(ywastrochart) 渲染成正版星座符号（与全站星盘一致），
// 不再用裸 Unicode '♈'（会被系统当成 emoji 渲染成彩色方块）。
const SECTORS = [
	{ rep: AstroConst.ARIES, name: '基本', fill: 'rgba(214,108,90,0.10)' },   // 基本宫代表：白羊
	{ rep: AstroConst.TAURUS, name: '固定', fill: 'rgba(96,150,104,0.10)' },  // 固定宫代表：金牛
	{ rep: AstroConst.GEMINI, name: '变动', fill: 'rgba(92,118,186,0.10)' },  // 变动宫代表：双子
];

// 概念环颜色（与本命区分；本命用图表描边色 currentColor）。
const RING_TONE = { natal: 'currentColor', transit: '#c0392b', solararc: '#1f7a5a' };
const POINTER_COLOR = '#e23b3b';

export default class UranianDial extends Component {
	constructor(props){
		super(props);
		this.svgid = 'uradial_' + randomStr(8);
		this.rotations = {};        // 每环旋转角（本命恒 0）
		this.pointerAngle = 0;      // 红指针显示角（0 = 正上）
		this._ringGroups = {};      // key -> {group, labels:[{node,x,y}], inner, outer}
		this._pointerG = null;
		this._drag = null;          // {type:'ring'|'pointer', key, base, ang0}
		this.draw = this.draw.bind(this);
		this._onMove = this._onMove.bind(this);
		this._onUp = this._onUp.bind(this);
	}
	componentDidMount(){ this.draw(); }
	componentDidUpdate(prev){
		if (prev.base !== this.props.base || prev.rings !== this.props.rings || prev.size !== this.props.size || prev.showTnp !== this.props.showTnp) {
			this.draw();
		}
	}
	componentWillUnmount(){ this._detach(); }

	rings(){ return (this.props.rings && this.props.rings.length) ? this.props.rings : [{ key: 'natal', label: '本命', points: this.props.points || [] }]; }

	// —— 屏幕坐标 → SVG 角度/半径（缩放无关：用 getBoundingClientRect 求中心 + 缩放比）——
	_metrics(evt){
		const node = document.getElementById(this.svgid);
		if (!node) return null;
		const r = node.getBoundingClientRect();
		const scale = r.width / (this.props.size || 600) || 1;
		const dx = evt.clientX - (r.left + r.width / 2);
		const dy = evt.clientY - (r.top + r.height / 2);
		return { ang: Math.atan2(-dx, -dy) * 180 / Math.PI, rad: Math.hypot(dx, dy) / scale };
	}

	emitReadout(){
		const { base, orb, personal, onlyPersonal } = this.props;
		const out = [];
		this.rings().forEach((ring) => {
			const rot = this.rotations[ring.key] || 0;
			// 指针所指处、该环内容对应的折叠黄经 = (指针角 − 环旋转) 映射回 0..base。
			const rel = norm360(this.pointerAngle - rot);
			const lonBase = ((rel / 360 * base) % base + base) % base;
			cursorReadout(ring.points || [], lonBase, base, orb, { personal, onlyPersonal }).forEach((h) => out.push({ ...h, ring: ring.label, ringKey: ring.key }));
		});
		out.sort((a, b) => a.sep - b.sep);
		if (this.props.onCursorChange) this.props.onCursorChange(out);
	}

	applyRingRotation(key, R, emit){
		this.rotations[key] = R;
		const cx = this._cx, cy = this._cy;
		const rg = this._ringGroups[key];
		if (!rg) return;
		// 逆时针盘：组用 rotate(-R)（d3 正角=顺时针），标签反向 rotate(R) 保持竖直；与 emitReadout 口径自洽。
		rg.group.attr('transform', `rotate(${-R}, ${cx}, ${cy})`);
		for (let i = 0; i < rg.labels.length; i++){ rg.labels[i].node.attr('transform', `rotate(${R}, ${rg.labels[i].x}, ${rg.labels[i].y})`); }
		// 太阳弧环拖动=向运：折叠盘旋转 R(显示度)对应黄道定向弧 = R*base/360(一圈=base 度)。
		// 仅在真实拖动(emit)时回调父级,否则初始 draw 期回调会触发父 setState→新 rings→重 draw 死循环。
		if (emit && key === 'solararc' && this.props.onSaArc){ this.props.onSaArc(((R % 360) + 360) % 360 * this.props.base / 360); }
	}
	applyPointerAngle(A){
		this.pointerAngle = A;
		if (this._pointerG) this._pointerG.attr('transform', `rotate(${-A}, ${this._cx}, ${this._cy})`);
	}

	_scheduleReadout(){ if (this._raf) cancelAnimationFrame(this._raf); this._raf = requestAnimationFrame(() => this.emitReadout()); }

	_attach(){ window.addEventListener('pointermove', this._onMove); window.addEventListener('pointerup', this._onUp); }
	_detach(){ window.removeEventListener('pointermove', this._onMove); window.removeEventListener('pointerup', this._onUp); }

	_onDown(evt){
		const m = this._metrics(evt);
		if (!m) return;
		const rings = this.rings();
		// 外圈刻度区(rad > Rin) → 拖红指针；某 transit/太阳弧环带内 → 拖该环；本命环锁定。
		if (m.rad > this._Rin){
			this._drag = { type: 'pointer', ang0: m.ang, base: this.pointerAngle };
		} else {
			let pick = null;
			for (const ring of rings){
				if (ring.key === 'natal') continue; // 本命锁定
				const rg = this._ringGroups[ring.key];
				if (rg && m.rad <= rg.outer + 4 && m.rad >= rg.inner - 4){ pick = ring.key; break; }
			}
			if (!pick) return;
			this._drag = { type: 'ring', key: pick, ang0: m.ang, base: this.rotations[pick] || 0 };
		}
		try { evt.target.setPointerCapture && evt.target.setPointerCapture(evt.pointerId); } catch (e) { /* noop */ }
		this._attach();
		d3.select('#' + this.svgid).style('cursor', 'grabbing');
	}
	_onMove(evt){
		if (!this._drag) return;
		const m = this._metrics(evt);
		if (!m) return;
		const delta = m.ang - this._drag.ang0;
		if (this._drag.type === 'pointer') this.applyPointerAngle(this._drag.base + delta);
		else this.applyRingRotation(this._drag.key, this._drag.base + delta, true);
		this._scheduleReadout();
	}
	_onUp(){ if (!this._drag) return; this._drag = null; this._detach(); d3.select('#' + this.svgid).style('cursor', 'grab'); this.emitReadout(); }

	draw(){
		const { base, showTnp } = this.props;
		const rings = this.rings();
		const size = this.props.size || 600;
		const cx = size / 2, cy = size / 2;
		this._cx = cx; this._cy = cy;
		const R = size / 2 - 14;
		const Rtick = R - 4;
		const Rin = Rtick - Math.max(26, size * 0.05);  // 刻度内缘 = 行星区外缘
		const Rnum = Rin + Math.max(13, size * 0.022);
		const Rhole = Math.max(46, Rin * 0.30);
		this._Rin = Rin;
		const stroke = 'currentColor';
		this._ringGroups = {};
		const svg = d3.select('#' + this.svgid);
		svg.selectAll('*').remove();
		const root = svg.append('g').attr('color', 'var(--horosa-chart-stroke, currentColor)');

		// —— 固定参考框架（不旋转）：外框 + 三模态扇区 + 细刻度 + 度数 ——
		root.append('circle').attr('cx', cx).attr('cy', cy).attr('r', R).attr('fill', 'none').attr('stroke', stroke).attr('stroke-width', 1.3).attr('opacity', 0.9);
		if (base === 90){
			SECTORS.forEach((s, bi) => {
				const a0 = (bi * 30) / 90 * TAU, a1 = ((bi + 1) * 30) / 90 * TAU;
				// 负角 = 逆时针，与 polar(逆时针)一致(d3.arc 正角为顺时针)。
				const arc = d3.arc().innerRadius(Rhole).outerRadius(Rin).startAngle(-a0).endAngle(-a1);
				root.append('path').attr('transform', `translate(${cx},${cy})`).attr('d', arc()).attr('fill', s.fill).attr('stroke', 'none');
				const [lx, ly] = polar(cx, cy, Rin, bi * 30 / 90 * 360);
				root.append('line').attr('x1', polar(cx, cy, Rhole, bi * 30 / 90 * 360)[0]).attr('y1', polar(cx, cy, Rhole, bi * 30 / 90 * 360)[1]).attr('x2', lx).attr('y2', ly).attr('stroke', stroke).attr('opacity', 0.14);
				const [gx, gy] = polar(cx, cy, Rhole * 0.62, (bi * 30 + 15) / 90 * 360);
				// 星座符号经 AstroMsg[名] 取字形码（与 signsBand 同源），再用 AstroChartFont 渲染成 ♈♉♊。
				root.append('text').attr('x', gx).attr('y', gy).attr('text-anchor', 'middle').attr('dominant-baseline', 'central').attr('font-size', Math.min(28, Rhole * 0.5)).attr('opacity', 0.34).attr('fill', AstroConst.AstroColor[s.rep] || stroke).attr('font-family', AstroConst.AstroChartFont).text(AstroText.AstroMsg[s.rep] || s.rep);
			});
		}
		root.append('circle').attr('cx', cx).attr('cy', cy).attr('r', Rtick).attr('fill', 'none').attr('stroke', stroke).attr('stroke-width', 0.9).attr('opacity', 0.6);
		root.append('circle').attr('cx', cx).attr('cy', cy).attr('r', Rin).attr('fill', 'none').attr('stroke', stroke).attr('stroke-width', 0.9).attr('opacity', 0.45);
		// 自适应刻度(支持任意盘基/谐波 H1..H512)：d3.ticks 取整齐主刻度,主刻度间均分次刻度;比旧版更明显。
		const majors = d3.ticks(0, base, 9);
		const majorStep = majors.length > 1 ? (majors[1] - majors[0]) : (base / 9);
		const minorStep = majorStep / 5;
		const fmtTick = (v) => { if (base >= 10) return `${Math.round(v)}`; const d = Math.floor(v + 1e-9); const m = Math.round((v - d) * 60); return m ? `${d}°${m}′` : `${d}°`; };
		for (let v = minorStep / 2; v < base - 1e-9; v += minorStep){
			const vis = v / base * 360;
			const [x1, y1] = polar(cx, cy, Rtick, vis), [x2, y2] = polar(cx, cy, Rtick - 8, vis);
			root.append('line').attr('x1', x1).attr('y1', y1).attr('x2', x2).attr('y2', y2).attr('stroke', stroke).attr('stroke-width', 0.7).attr('opacity', 0.42);
		}
		majors.forEach((v) => {
			if (v >= base - 1e-9) return; // base 处与 0 重合,跳过
			const vis = v / base * 360;
			const [x1, y1] = polar(cx, cy, Rtick, vis), [x2, y2] = polar(cx, cy, Rtick - 20, vis);
			root.append('line').attr('x1', x1).attr('y1', y1).attr('x2', x2).attr('y2', y2).attr('stroke', stroke).attr('stroke-width', 1.3).attr('opacity', 0.85);
			const [lx, ly] = polar(cx, cy, Rnum, vis);
			root.append('text').attr('x', lx).attr('y', ly).attr('dy', '0.35em').attr('text-anchor', 'middle').attr('font-size', Math.max(10, size * 0.016)).attr('fill', stroke).attr('opacity', 0.75).text(fmtTick(v));
		});

		// —— 旋转：每环行星带（本命=最内圈，行运/太阳弧依次向外，符合标准三重叠盘约定）——
		const band = (Rin - Rhole - 8);
		const per = band / rings.length;
		rings.forEach((ring, ri) => {
			const rInner = Rhole + 8 + ri * per;
			const rOuter = rInner + per;
			const rPlanet = (rOuter + rInner) / 2 + per * 0.06;
			const rDot = rOuter - 2;
			const tone = RING_TONE[ring.key] || stroke;
			const g = root.append('g').style('cursor', ring.key === 'natal' ? 'default' : 'grab');
			const labels = [];
			g.append('circle').attr('cx', cx).attr('cy', cy).attr('r', rOuter).attr('fill', 'none').attr('stroke', tone).attr('stroke-width', 0.6).attr('opacity', 0.22);
			const visible = (ring.points || []).filter((p) => showTnp || !AstroText.isUranian(p.id));
			const baseSz = Math.min(19, Math.max(13, per * 0.26));
			// 防重叠:挤一起的字形沿环顶开,字形画在避让位、真位画小点、两者连线(同全站星盘 desposeStars)。
			const minGap = Math.min(20, (baseSz * 1.25) / Math.max(40, rPlanet) * 180 / Math.PI);
			const placed = spreadDialAngles(visible.map((p) => ({ p, displayAngle: projectToDial(p.lon, base) })), minGap);
			placed.forEach((item) => {
				const p = item.p;
				const [px, py] = polar(cx, cy, rOuter, item.displayAngle);   // 环上真位
				const [lx, ly] = polar(cx, cy, rPlanet, item.glyphAngle);    // 避让后字形位
				// 白羊点用全站星盘的 Aries 字形(AstroMsg['Aries']+AstroChartFont)，不用裸 '♈'(emoji)；TNP 才走缩写。
				const tnp = AstroText.isUranian(p.id) && p.id !== AstroConst.ARIES_POINT;
				const glyphCh = tnp ? AstroText.uranianGlyph(p.id)
					: (p.id === AstroConst.ARIES_POINT ? AstroText.AstroMsg[AstroConst.ARIES] : (AstroText.AstroMsg[p.id] || AstroText.uranianGlyph(p.id)));
				g.append('line').attr('x1', px).attr('y1', py).attr('x2', lx).attr('y2', ly).attr('stroke', tone).attr('stroke-width', 0.7).attr('opacity', 0.42);
				g.append('circle').attr('cx', px).attr('cy', py).attr('r', 1.9).attr('fill', tone).attr('opacity', 0.85);
				const gl = g.append('text').attr('x', lx).attr('y', ly).attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
					.attr('font-size', tnp ? baseSz * 0.78 : baseSz).attr('fill', tone)
					.attr('font-family', tnp ? 'inherit' : AstroConst.AstroChartFont).attr('font-weight', tnp ? 600 : 400)
					.style('letter-spacing', tnp ? '0.3px' : '0').style('pointer-events', 'none')
					.text(glyphCh);
				gl.append('title').text(ring.label + ' · ' + (AstroText.AstroMsgCN[p.id] || p.id));
				labels.push({ node: gl, x: lx, y: ly });
			});
			this._ringGroups[ring.key] = { group: g, labels, inner: rInner, outer: rOuter, rPlanet };
			this.rotations[ring.key] = this.rotations[ring.key] || 0;
		});

		// 中心 hub
		root.append('circle').attr('cx', cx).attr('cy', cy).attr('r', 3.2).attr('fill', stroke).attr('opacity', 0.5);

		// —— 可拖红指针（含东西 ±22.5° 标记）——
		const pg = root.append('g').style('cursor', 'grab');
		this._pointerG = pg;
		const drawArrow = (group, deg, col, w, op) => {
			const [tipx, tipy] = polar(cx, cy, R + 3, deg), [bx, by] = polar(cx, cy, R - 16, deg);
			const a = deg / 360 * TAU, perp = a + Math.PI / 2;
			group.append('line').attr('x1', cx).attr('y1', cy).attr('x2', bx).attr('y2', by).attr('stroke', col).attr('stroke-width', w).attr('opacity', op);
			group.append('polygon').attr('points', `${tipx},${tipy} ${bx + 7 * Math.cos(perp)},${by + 7 * Math.sin(perp)} ${bx - 7 * Math.cos(perp)},${by - 7 * Math.sin(perp)}`).attr('fill', col).attr('opacity', op);
		};
		drawArrow(pg, 0, POINTER_COLOR, 1.6, 0.9);
		drawArrow(pg, 180, POINTER_COLOR, 1.2, 0.5);
		// 东西 22.5° 标记（物理 ±90°，= 16 分相族半个 45°，spec §4.3）
		[22.5, -22.5, 157.5, 202.5].forEach((d) => {
			const [a1, b1] = [polar(cx, cy, R, d), polar(cx, cy, R - 12, d)];
			pg.append('line').attr('x1', a1[0]).attr('y1', a1[1]).attr('x2', b1[0]).attr('y2', b1[1]).attr('stroke', POINTER_COLOR).attr('stroke-width', 1).attr('opacity', 0.45);
		});
		// 指针外圈抓手（在外刻度区，明示可拖）
		const [hx, hy] = polar(cx, cy, R - 6, 0);
		pg.append('circle').attr('cx', hx).attr('cy', hy).attr('r', 5).attr('fill', POINTER_COLOR).attr('opacity', 0.92).append('title').text('拖动红指针扫描对齐');

		// —— 单一透明命中层接管 pointerdown（外圈拖指针 / 环带拖该环）——
		const hit = root.append('circle').attr('cx', cx).attr('cy', cy).attr('r', R).attr('fill', 'transparent').style('cursor', 'grab').style('pointer-events', 'all');
		hit.node().addEventListener('pointerdown', (e) => { e.preventDefault(); this._onDown(e); });

		rings.forEach((ring) => this.applyRingRotation(ring.key, this.rotations[ring.key] || 0));
		this.applyPointerAngle(this.pointerAngle);

		// 多环图例
		if (rings.length > 1){
			const legend = root.append('g');
			rings.forEach((ring, ri) => {
				const ly = 12 + ri * 16;
				const tone = RING_TONE[ring.key] === 'currentColor' ? stroke : (RING_TONE[ring.key] || stroke);
				legend.append('circle').attr('cx', 10).attr('cy', ly).attr('r', 4).attr('fill', tone).attr('opacity', 0.9);
				legend.append('text').attr('x', 19).attr('y', ly).attr('dy', '0.35em').attr('font-size', 11).attr('fill', stroke).attr('opacity', 0.78).text(ring.label + (ring.key === 'natal' ? '（锁定）' : ''));
			});
			legend.append('text').attr('x', 10).attr('y', 12 + rings.length * 16 + 4).attr('dy', '0.35em').attr('font-size', 10).attr('fill', stroke).attr('opacity', 0.5).text('拖行运/太阳弧环或红指针');
		}
	}

	render(){
		const size = this.props.size || 600;
		// textRendering:geometricPrecision + liga 开启 ywastrochart 的「星座名→符号」连字（与全站星盘一致），
		// 否则扇区里的 Aries/Taurus/Gemini 会按原文 5 字母渲染而非 ♈♉♊ 字形。
		return <svg id={this.svgid} width={size} height={size} className="horosa-uranian-dial xq-chart-renderer xq-chart-renderer-astro" style={{ maxWidth: '100%', display: 'block', margin: '0 auto', touchAction: 'none', textRendering: 'geometricPrecision', fontFeatureSettings: '"liga" 1, "dlig" 1, "calt" 1' }} />;
	}
}
