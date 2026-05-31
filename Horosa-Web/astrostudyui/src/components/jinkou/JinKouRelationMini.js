// 金口诀 · 地支刑冲合害破 关系图（独立 SVG，不耦合主盘 JinKouPanChart）
import { Component } from 'react';

const ZI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

function ptOf(i, cx, cy, r){
	const ang = (-90 + i * 30) * Math.PI / 180;
	return { x: cx + r * Math.cos(ang), y: cy + r * Math.sin(ang) };
}

class JinKouRelationMini extends Component {
	render(){
		const relations = this.props.relations || [];
		const rows = this.props.rows || [];
		const size = 180;
		const cx = 90;
		const cy = 90;
		const r = 66;
		const four = {};
		rows.forEach((row)=>{ if(row && row.branch){ four[row.branch] = row.label; } });
		const colorOf = (t)=>((t === '合' || t === '三合') ? '#2f9f68' : (t === '冲' ? '#d64a35' : '#c98a2f'));
		const dashedOf = (t)=>(t === '刑' || t === '害' || t === '破');
		return (
			<svg viewBox={`0 0 ${size} ${size}`} width="100%" height="186" style={{ display: 'block', margin: '0 auto' }}>
				<circle cx={cx} cy={cy} r={r} fill="none" stroke="var(--horosa-border, #e0d9c0)" strokeWidth="1" />
				{relations.map((rel, k)=>{
					const ia = ZI.indexOf(rel.a);
					const ib = ZI.indexOf(rel.b);
					if(ia < 0 || ib < 0){ return null; }
					const pa = ptOf(ia, cx, cy, r);
					const pb = ptOf(ib, cx, cy, r);
					return (
						<line
							key={`rel_${k}`}
							x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y}
							stroke={colorOf(rel.type)} strokeWidth="1.6"
							strokeDasharray={dashedOf(rel.type) ? '4 3' : ''} opacity="0.8"
						>
							<title>{`${rel.a}${rel.type}${rel.b}`}</title>
						</line>
					);
				})}
				{ZI.map((zi, i)=>{
					const p = ptOf(i, cx, cy, r);
					const hit = four[zi];
					return (
						<g key={`zi_${zi}`}>
							<circle
								cx={p.x} cy={p.y} r={hit ? 11 : 8}
								fill={hit ? 'var(--horosa-gold-soft, #f7f3dc)' : 'transparent'}
								stroke={hit ? '#c98a2f' : 'var(--horosa-border, #d9d9d9)'} strokeWidth="1"
							/>
							<text
								x={p.x} y={p.y + 4} textAnchor="middle" fontSize="11"
								fill={hit ? '#8a5a17' : 'var(--horosa-text-soft, #595959)'} fontWeight={hit ? 600 : 400}
							>{zi}</text>
							{hit ? (
								<text x={p.x} y={p.y - 14} textAnchor="middle" fontSize="9" fill="var(--horosa-muted, #8c8c8c)">{hit}</text>
							) : null}
						</g>
					);
				})}
			</svg>
		);
	}
}

export default JinKouRelationMini;
