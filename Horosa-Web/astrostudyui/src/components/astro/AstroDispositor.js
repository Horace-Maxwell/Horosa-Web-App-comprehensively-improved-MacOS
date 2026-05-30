// components/astro/AstroDispositor.js
// 主宰星链（dispositor chains）+ 宫神星（各宫主星及其落点）。纯前端派生，嵌于本命「古典」tab。
import { Component } from 'react';
import { astroSymbol, cardStyle, SmallTable } from './AstroExtraCommon';
import { SIGNS, SIGN_ORDER } from '../../divination/data/signs';
import { chartIdOfKey, keyOfChartId } from '../../divination/engine/utils';

function norm360(x){ return ((x % 360) + 360) % 360; }
function signOf(lon){ return SIGN_ORDER[Math.floor(norm360(lon) / 30)]; }
const sn = (s) => (SIGNS[s] && SIGNS[s].cn) || s || '-';
const symKey = (k) => astroSymbol(chartIdOfKey(k) || k);
const houseNum = (id) => { const m = /House\s*(\d+)/.exec(String(id || '')); return m ? parseInt(m[1], 10) : null; };
const TRAD = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn'];

class AstroDispositor extends Component {
	render(){
		const chartObj = this.props.value;
		if(!chartObj || !chartObj.chart) return null;
		// 行星落点 key -> {sign, house}
		const pos = {};
		(chartObj.chart.objects || []).forEach((o) => {
			if(!o || !o.id) return;
			const k = keyOfChartId(o.id);
			const sign = o.sign ? String(o.sign).toLowerCase() : (o.lon != null ? signOf(o.lon) : null);
			pos[k] = { sign, house: houseNum(o.house) };
		});
		// 单步主宰：行星 → 其所落星座的本垣主
		const step = {};
		TRAD.forEach((k) => { const p = pos[k]; if(p && p.sign) step[k] = (SIGNS[p.sign] || {}).domicile || null; });
		// 走链：至自指(终极主宰)或成环(互容)
		const chains = {}; const finals = new Set(); const loops = [];
		TRAD.forEach((start) => {
			if(step[start] === undefined) return;
			const path = []; const seen = new Set(); let cur = start;
			while(cur && step[cur] !== undefined){
				if(seen.has(cur)){ loops.push(path.slice(path.indexOf(cur))); path.push(cur); break; }
				seen.add(cur); path.push(cur);
				const nxt = step[cur];
				if(nxt === cur){ finals.add(cur); break; }
				cur = nxt;
			}
			chains[start] = path;
		});
		const seenLoop = new Set(); const uniqLoops = [];
		loops.forEach((c) => { const key = [...c].sort().join('>'); if(!seenLoop.has(key)){ seenLoop.add(key); uniqLoops.push(c); } });
		// 宫神星：各宫头星座的本垣主 + 该主星落宫/落座
		const houseRows = [];
		(chartObj.chart.houses || []).forEach((h) => {
			if(!h) return;
			const hn = houseNum(h.id);
			if(!hn) return;
			const csign = h.sign ? String(h.sign).toLowerCase() : (h.lon != null ? signOf(h.lon) : null);
			const ruler = csign ? (SIGNS[csign] || {}).domicile || null : null;
			const rp = ruler ? pos[ruler] : null;
			houseRows.push({ house: hn, sign: csign, ruler, rulerSign: rp ? rp.sign : null, rulerHouse: rp ? rp.house : null });
		});
		houseRows.sort((a, b) => a.house - b.house);
		return (
			<div style={cardStyle}>
				<div style={{ fontWeight: 600, marginBottom: 8, fontSize: 13 }}>主宰星链 与 宫神星</div>
				<div style={{ fontSize: 12, lineHeight: 2 }}>
					{TRAD.filter((k) => chains[k] && chains[k].length).map((k) => (
						<div key={k}>{chains[k].map((x, i) => <span key={i}>{i > 0 ? <span style={{ margin: '0 4px' }}>→</span> : null}{symKey(x)}</span>)}</div>
					))}
				</div>
				<div style={{ fontSize: 12, marginTop: 8 }}>最终主宰：{finals.size ? [...finals].map((k, i) => <span key={i} style={{ marginRight: 6 }}>{symKey(k)}</span>) : '无（全部成环）'}</div>
				{uniqLoops.length ? <div style={{ fontSize: 12, marginTop: 4 }}>互容环：{uniqLoops.map((c, i) => <span key={i} style={{ marginRight: 10 }}>{c.map((x, j) => <span key={j}>{j > 0 ? ' ↔ ' : ''}{symKey(x)}</span>)}</span>)}</div> : null}
				<div style={{ marginTop: 10 }}>
					<SmallTable
						rowKey={(r) => r.house}
						rows={houseRows}
						columns={[
							{ key: 'house', title: '宫', render: (v) => `${v}宫` },
							{ key: 'sign', title: '宫头', render: (v) => sn(v) },
							{ key: 'ruler', title: '宫主星', render: (v) => (v ? symKey(v) : '-') },
							{ key: 'rulerHouse', title: '宫主落宫', render: (v) => (v ? `${v}宫` : '-') },
							{ key: 'rulerSign', title: '宫主落座', render: (_v, r) => (r.rulerSign ? sn(r.rulerSign) : '-') },
						]}
					/>
				</div>
			</div>
		);
	}
}

export default AstroDispositor;
