import { Component } from 'react';
import * as d3 from 'd3';
import { randomStr } from '../../utils/helper';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { cursorReadout, spreadDialAngles } from '../../utils/uranianDial';

// 真 360° 多环模数盘（与折叠盘并列的另一种汉堡技法）：三层同心环按真实黄道位置画行星，
// 中央叠一圈可读的模数刻度盘 + 可拖红指针；除本命外每环可拖动旋转，拖指针/环读「指针所指真实度数」
// 与「该度数在所选模数(默认90°)下、orb 内对齐的中点/行星图」。对齐判定与折叠盘共用 uranianDial 引擎。

const TAU = Math.PI * 2;
const norm360 = (x) => ((x % 360) + 360) % 360;
// 逆时针(0°在正上、度数向左增)，与全站星盘一致。
const polar = (cx, cy, R, deg) => { const a = deg / 360 * TAU; return [cx - R * Math.sin(a), cy - R * Math.cos(a)]; };
const RING_TONE = { natal: 'currentColor', transit: '#c0392b', solararc: '#1f7a5a' };
const POINTER_COLOR = '#e23b3b';

export default class UranianModulusDial extends Component {
	constructor(props){
		super(props);
		this.svgid = 'uramod_' + randomStr(8);
		this.rotations = {};
		this.pointerAngle = 0;
		this._ringGroups = {};
		this._pointerG = null;
		this._drag = null;
		this.draw = this.draw.bind(this);
		this._onMove = this._onMove.bind(this);
		this._onUp = this._onUp.bind(this);
	}
	componentDidMount(){ this.draw(); }
	componentDidUpdate(prev){
		if (prev.base !== this.props.base || prev.rings !== this.props.rings || prev.size !== this.props.size || prev.showTnp !== this.props.showTnp) this.draw();
	}
	componentWillUnmount(){ this._detach(); }

	rings(){ return (this.props.rings && this.props.rings.length) ? this.props.rings : [{ key: 'natal', label: '本命', points: this.props.points || [] }]; }

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
			// 真位盘：显示角=真实黄经，环旋转 rot 后行星真实角 = lon+rot；指针真实角=pointerAngle。
			// 折叠对齐的 cursor 黄经 = (pointerAngle − rot)，交给同一 cursorReadout（内部按 base 折叠）。
			const cursorLon = norm360(this.pointerAngle - rot);
			cursorReadout(ring.points || [], cursorLon, base, orb, { personal, onlyPersonal }).forEach((h) => out.push({ ...h, ring: ring.label, ringKey: ring.key }));
		});
		out.sort((a, b) => a.sep - b.sep);
		if (this.props.onCursorChange) this.props.onCursorChange(out);
	}

	applyRingRotation(key, R, emit){
		this.rotations[key] = R;
		const rg = this._ringGroups[key];
		if (!rg) return;
		// 逆时针盘：组 rotate(-R)、标签反向 rotate(R)；与 emitReadout 口径自洽。
		rg.group.attr('transform', `rotate(${-R}, ${this._cx}, ${this._cy})`);
		for (let i = 0; i < rg.labels.length; i++){ rg.labels[i].node.attr('transform', `rotate(${R}, ${rg.labels[i].x}, ${rg.labels[i].y})`); }
		// 太阳弧环拖动=向运：真位盘旋转 R(显示度)=黄道定向弧 R(1:1)。仅真实拖动(emit)回调,避免初始 draw 死循环。
		if (emit && key === 'solararc' && this.props.onSaArc){ this.props.onSaArc(((R % 360) + 360) % 360); }
	}
	applyPointerAngle(A){
		this.pointerAngle = A;
		if (this._pointerG) this._pointerG.attr('transform', `rotate(${-A}, ${this._cx}, ${this._cy})`);
		if (this._degText) this._degText.text(`${norm360(A).toFixed(1)}° · 模 ${(norm360(A) % this.props.base).toFixed(1)}°`);
	}
	_scheduleReadout(){ if (this._raf) cancelAnimationFrame(this._raf); this._raf = requestAnimationFrame(() => this.emitReadout()); }
	_attach(){ window.addEventListener('pointermove', this._onMove); window.addEventListener('pointerup', this._onUp); }
	_detach(){ window.removeEventListener('pointermove', this._onMove); window.removeEventListener('pointerup', this._onUp); }

	_onDown(evt){
		const m = this._metrics(evt);
		if (!m) return;
		if (m.rad > this._Rringtop){
			this._drag = { type: 'pointer', ang0: m.ang, base: this.pointerAngle };
		} else {
			let pick = null;
			for (const ring of this.rings()){
				if (ring.key === 'natal') continue;
				const rg = this._ringGroups[ring.key];
				if (rg && m.rad <= rg.outer + 4 && m.rad >= rg.inner - 4){ pick = ring.key; break; }
			}
			if (!pick) { this._drag = { type: 'pointer', ang0: m.ang, base: this.pointerAngle }; }
			else this._drag = { type: 'ring', key: pick, ang0: m.ang, base: this.rotations[pick] || 0 };
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
		const Rsign = R - Math.max(22, size * 0.034);
		const Rringtop = Rsign - 14;
		this._Rringtop = Rringtop;
		const Rmod = Math.max(58, size * 0.14);
		const stroke = 'currentColor';
		this._ringGroups = {};
		const svg = d3.select('#' + this.svgid);
		svg.selectAll('*').remove();
		const root = svg.append('g').attr('color', 'var(--horosa-chart-stroke, currentColor)');

		// —— 固定外框：360° 圈 + 12 星座字形 + 每 30° 分隔 + 度刻度 ——
		root.append('circle').attr('cx', cx).attr('cy', cy).attr('r', R).attr('fill', 'none').attr('stroke', stroke).attr('stroke-width', 1.3).attr('opacity', 0.9);
		root.append('circle').attr('cx', cx).attr('cy', cy).attr('r', Rsign + 1).attr('fill', 'none').attr('stroke', stroke).attr('stroke-width', 0.8).attr('opacity', 0.4);
		for (let s = 0; s < 12; s++){
			const sigName = AstroConst.LIST_SIGNS[s];
			const a0 = s * 30;
			const [lx, ly] = polar(cx, cy, Rsign - (Rsign - Rringtop) * 0.5 + 6, a0 + 15);
			root.append('text').attr('x', lx).attr('y', ly).attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
				.attr('font-size', Math.max(13, size * 0.02)).attr('font-family', AstroConst.AstroChartFont)
				.attr('fill', AstroConst.AstroColor[sigName] || stroke).attr('opacity', 0.7).text(AstroText.AstroMsg[sigName] || '');
			const [bx, by] = polar(cx, cy, R, a0), [bx2, by2] = polar(cx, cy, Rringtop, a0);
			root.append('line').attr('x1', bx).attr('y1', by).attr('x2', bx2).attr('y2', by2).attr('stroke', stroke).attr('stroke-width', 0.7).attr('opacity', 0.3);
		}
		for (let k = 0; k < 360; k += 1){
			const isLong = (k % 30 === 0), isMed = (k % 10 === 0);
			if (!isMed && size < 620) continue;
			const r2 = Rtick - (isLong ? 9 : isMed ? 6 : 3);
			const [x1, y1] = polar(cx, cy, Rtick, k), [x2, y2] = polar(cx, cy, r2, k);
			root.append('line').attr('x1', x1).attr('y1', y1).attr('x2', x2).attr('y2', y2).attr('stroke', stroke).attr('stroke-width', isLong ? 1.2 : 0.6).attr('opacity', isLong ? 0.8 : isMed ? 0.5 : 0.28);
			if (isLong){ const [nx, ny] = polar(cx, cy, Rtick - 16, k); root.append('text').attr('x', nx).attr('y', ny).attr('dy', '0.35em').attr('text-anchor', 'middle').attr('font-size', 9).attr('fill', stroke).attr('opacity', 0.7).text(k); }
		}

		// —— 旋转：每环行星带（真实黄道位置；本命=最内圈，行运/太阳弧向外）——
		const band = Rringtop - Rmod - 12;
		const per = band / rings.length;
		rings.forEach((ring, ri) => {
			const rInner = Rmod + 12 + ri * per;
			const rOuter = rInner + per;
			const rPlanet = (rOuter + rInner) / 2;
			const tone = RING_TONE[ring.key] || stroke;
			const g = root.append('g').style('cursor', ring.key === 'natal' ? 'default' : 'grab');
			const labels = [];
			g.append('circle').attr('cx', cx).attr('cy', cy).attr('r', rOuter).attr('fill', 'none').attr('stroke', tone).attr('stroke-width', 0.6).attr('opacity', 0.22);
			const visible = (ring.points || []).filter((p) => showTnp || !AstroText.isUranian(p.id));
			const baseSz = Math.min(18, Math.max(12, per * 0.36));
			const minGap = Math.min(16, (baseSz * 1.25) / Math.max(60, rPlanet) * 180 / Math.PI);
			const placed = spreadDialAngles(visible.map((p) => ({ p, displayAngle: norm360(p.lon) })), minGap);
			placed.forEach((item) => {
				const p = item.p;
				const [px, py] = polar(cx, cy, rOuter, item.displayAngle);   // 真实黄道位
				const [lx, ly] = polar(cx, cy, rPlanet, item.glyphAngle);    // 避让后字形
				const tnp = AstroText.isUranian(p.id) && p.id !== AstroConst.ARIES_POINT;
				const glyphCh = tnp ? AstroText.uranianGlyph(p.id)
					: (p.id === AstroConst.ARIES_POINT ? AstroText.AstroMsg[AstroConst.ARIES] : (AstroText.AstroMsg[p.id] || AstroText.uranianGlyph(p.id)));
				g.append('line').attr('x1', px).attr('y1', py).attr('x2', lx).attr('y2', ly).attr('stroke', tone).attr('stroke-width', 0.7).attr('opacity', 0.42);
				g.append('circle').attr('cx', px).attr('cy', py).attr('r', 1.8).attr('fill', tone).attr('opacity', 0.85);
				const gl = g.append('text').attr('x', lx).attr('y', ly).attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
					.attr('font-size', tnp ? baseSz * 0.8 : baseSz).attr('fill', tone)
					.attr('font-family', tnp ? 'inherit' : AstroConst.AstroChartFont).attr('font-weight', tnp ? 600 : 400)
					.style('letter-spacing', tnp ? '0.3px' : '0').style('pointer-events', 'none')
					.text(glyphCh);
				gl.append('title').text(ring.label + ' · ' + (AstroText.AstroMsgCN[p.id] || p.id) + ' ' + norm360(p.lon).toFixed(2) + '°');
				labels.push({ node: gl, x: lx, y: ly });
			});
			this._ringGroups[ring.key] = { group: g, labels, inner: rInner, outer: rOuter };
			this.rotations[ring.key] = this.rotations[ring.key] || 0;
		});

		// —— 中央模数刻度盘（0..base 绕一圈，读指针折叠位）——
		root.append('circle').attr('cx', cx).attr('cy', cy).attr('r', Rmod).attr('fill', 'var(--horosa-card-bg, rgba(255,255,255,0.6))').attr('stroke', stroke).attr('stroke-width', 0.8).attr('opacity', 0.85);
		// 内圈模数刻度自适应(支持任意谐波)：d3.ticks 取整齐主刻度 + 均分次刻度。
		const modMajors = d3.ticks(0, base, 9);
		const modMajorStep = modMajors.length > 1 ? (modMajors[1] - modMajors[0]) : (base / 9);
		const modMinorStep = modMajorStep / 5;
		const fmtMod = (v) => { if (base >= 10) return `${Math.round(v)}`; const d = Math.floor(v + 1e-9); const m = Math.round((v - d) * 60); return m ? `${d}°${m}′` : `${d}°`; };
		for (let v = modMinorStep / 2; v < base - 1e-9; v += modMinorStep){
			const a = v / base * 360;
			const [x1, y1] = polar(cx, cy, Rmod, a), [x2, y2] = polar(cx, cy, Rmod - 5, a);
			root.append('line').attr('x1', x1).attr('y1', y1).attr('x2', x2).attr('y2', y2).attr('stroke', stroke).attr('stroke-width', 0.5).attr('opacity', 0.35);
		}
		modMajors.forEach((v) => {
			if (v >= base - 1e-9) return;
			const a = v / base * 360;
			const [x1, y1] = polar(cx, cy, Rmod, a), [x2, y2] = polar(cx, cy, Rmod - 9, a);
			root.append('line').attr('x1', x1).attr('y1', y1).attr('x2', x2).attr('y2', y2).attr('stroke', stroke).attr('stroke-width', 1).attr('opacity', 0.7);
			const [nx, ny] = polar(cx, cy, Rmod - 17, a); root.append('text').attr('x', nx).attr('y', ny).attr('dy', '0.35em').attr('text-anchor', 'middle').attr('font-size', 8.5).attr('fill', stroke).attr('opacity', 0.65).text(fmtMod(v));
		});
		root.append('text').attr('x', cx).attr('y', cy - 7).attr('text-anchor', 'middle').attr('font-size', 10).attr('fill', stroke).attr('opacity', 0.5).text(`${base}° 模数`);
		this._degText = root.append('text').attr('x', cx).attr('y', cy + 9).attr('text-anchor', 'middle').attr('font-size', 11).attr('font-weight', 600).attr('fill', POINTER_COLOR).attr('opacity', 0.9);

		// —— 可拖红指针 ——
		const pg = root.append('g').style('cursor', 'grab');
		this._pointerG = pg;
		const [tipx, tipy] = polar(cx, cy, R + 3, 0), [bx, by] = polar(cx, cy, Rmod, 0);
		pg.append('line').attr('x1', cx).attr('y1', Rmod ? (cy - Rmod) : cy).attr('x2', tipx).attr('y2', tipy).attr('stroke', POINTER_COLOR).attr('stroke-width', 1.6).attr('opacity', 0.9);
		pg.append('polygon').attr('points', `${tipx},${tipy} ${tipx - 5},${tipy + 11} ${tipx + 5},${tipy + 11}`).attr('fill', POINTER_COLOR);
		const [hx, hy] = polar(cx, cy, R - 6, 0);
		pg.append('circle').attr('cx', hx).attr('cy', hy).attr('r', 5).attr('fill', POINTER_COLOR).attr('opacity', 0.92).append('title').text('拖动红指针扫描');

		const hit = root.append('circle').attr('cx', cx).attr('cy', cy).attr('r', R).attr('fill', 'transparent').style('cursor', 'grab').style('pointer-events', 'all');
		hit.node().addEventListener('pointerdown', (e) => { e.preventDefault(); this._onDown(e); });

		rings.forEach((ring) => this.applyRingRotation(ring.key, this.rotations[ring.key] || 0));
		this.applyPointerAngle(this.pointerAngle);

		// 图例
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
		return <svg id={this.svgid} width={size} height={size} className="horosa-uranian-dial xq-chart-renderer xq-chart-renderer-astro" style={{ maxWidth: '100%', display: 'block', margin: '0 auto', touchAction: 'none', textRendering: 'geometricPrecision', fontFeatureSettings: '"liga" 1, "dlig" 1, "calt" 1' }} />;
	}
}
