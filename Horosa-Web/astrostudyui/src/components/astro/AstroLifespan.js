// components/astro/AstroLifespan.js
// 古典寿命格局面板（生命主/寿主星寿数/盘主体系/行星状态/医疗危机）。
// 纯前端：buildFacts(本命chartObj) → runLifespan；嵌于本命「古典」tab 底部，不新开 tab。
import { Component } from 'react';
import buildFacts from '../../divination/engine/chartFacts';
import { runLifespan } from '../../divination/lifespan/lifespanEngine';
import { SIGNS } from '../../divination/data/signs';
import { chartIdOfKey } from '../../divination/engine/utils';
import { astroSymbol, fmtNum, cardStyle, SmallTable } from './AstroExtraCommon';

const METHODS = [
	{ value: 'ptolemy', label: '托勒密' },
	{ value: 'alcabitius', label: '阿尔卡比修斯' },
	{ value: 'dorotheus', label: '多罗修斯' },
];
const DIGNITY_CN = { domicile: '本垣', exaltation: '擢升', triplicity: '三分', term: '界', face: '十度' };
const BAND_CN = { greatest: '大限', mean: '中限', least: '小限' };
const HAYYIZ_CN = { Hayyiz: '得时得地', DemiHayyiz: '得时不得地', InWrongPos: '失位', None: '—' };
const SUNSTATE_CN = { cazimi: '日心', combust: '焦伤', under_beams: '日光束下' };
const ORIENT_CN = { oriental: '东出', occidental: '西入' };

const sym = (key) => astroSymbol(chartIdOfKey(key) || key);
const sn = (sign) => (SIGNS[sign] && SIGNS[sign].cn) || sign || '-';
const degText = (signlon) => (signlon == null ? '-' : `${fmtNum(signlon, 1)}°`);
const houseText = (h) => (h ? `${h}宫` : '-');
const posText = (sign, signlon) => `${sn(sign)} ${degText(signlon)}`;

// 把本命 chartObj 补出 objectMap/houseMap（buildFacts 需要；与 AstroHelper 惰性缓存同款，不依赖它）
function ensureMaps(chartObj){
	if(!chartObj || !chartObj.chart) return chartObj;
	if(!chartObj.objectMap && Array.isArray(chartObj.chart.objects)){
		const m = {};
		chartObj.chart.objects.forEach((o) => { if(o && o.id) m[o.id] = o; });
		chartObj.objectMap = m;
	}
	if(!chartObj.houseMap && Array.isArray(chartObj.chart.houses)){
		const hm = {};
		chartObj.chart.houses.forEach((h) => { if(h && h.id) hm[h.id] = h; });
		chartObj.houseMap = hm;
	}
	return chartObj;
}

const sectionTitle = { fontWeight: 600, marginBottom: 8, fontSize: 13 };
const kv = { display: 'flex', flexWrap: 'wrap', gap: '4px 16px', fontSize: 12, lineHeight: 1.9 };

class AstroLifespan extends Component {
	constructor(props){
		super(props);
		this.state = { method: 'ptolemy' };
	}

	render(){
		const chartObj = this.props.value;
		if(!chartObj || !chartObj.chart){
			return <div style={{ padding: 12, fontSize: 12, opacity: 0.7 }}>暂无本命盘数据</div>;
		}
		let res = null;
		try{
			const facts = buildFacts(ensureMaps(chartObj));
			res = facts ? runLifespan(facts, { method: this.state.method }) : null;
		}catch(e){
			return <div style={{ padding: 12, fontSize: 12, color: '#c0392b' }}>寿命格局计算出错：{String(e && e.message || e)}</div>;
		}
		if(!res){ return <div style={{ padding: 12, fontSize: 12, opacity: 0.7 }}>无法解析本命盘</div>; }

		const hy = res.hyleg;
		const alc = res.alcocoden;

		return (
			<div style={{ paddingRight: 6 }}>
				{/* 作者选择 */}
				<div style={{ ...cardStyle, display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
					<span style={{ fontWeight: 600, fontSize: 13 }}>寿命格局</span>
					<span style={{ fontSize: 12, opacity: 0.7 }}>取主法：</span>
					{METHODS.map((m) => (
						<span
							key={m.value}
							onClick={() => this.setState({ method: m.value })}
							style={{
								cursor: 'pointer', fontSize: 12, padding: '2px 10px', borderRadius: 6,
								border: '1px solid rgba(148,163,184,.4)',
								background: this.state.method === m.value ? 'var(--horosa-accent, #6c5ce7)' : 'transparent',
								color: this.state.method === m.value ? '#fff' : 'inherit',
							}}
						>{m.label}</span>
					))}
					<span style={{ fontSize: 12, opacity: 0.7, marginLeft: 'auto' }}>
						{res.isDiurnal ? '日生盘' : '夜生盘'} · {res.birthType === 'conjunctional' ? '朔月型' : '望月型'}
					</span>
				</div>

				{/* 生命主候选 */}
				<div style={cardStyle}>
					<div style={sectionTitle}>生命主（Hyleg）{hy ? <span>　→　{sym(hy.key)} {posText(hy.sign, hy.signlon)}（{houseText(hy.house)}）</span> : '　→　未定'}</div>
					<SmallTable
						rowKey={(r) => r.key}
						rows={res.candidates}
						columns={[
							{ key: 'key', title: '候选点', render: (v) => sym(v) },
							{ key: 'house', title: '宫位', render: (v) => houseText(v) },
							{ key: 'aphetic', title: '释放位', render: (v) => (v ? '✓' : '—') },
							{ key: 'rank', title: '权重', render: (v) => (v == null ? '-' : v) },
							{ key: 'reason', title: '判定', render: (v) => <span style={{ opacity: 0.85 }}>{v}</span> },
						]}
					/>
				</div>

				{/* 寿主星与寿数 */}
				<div style={cardStyle}>
					<div style={sectionTitle}>寿主星（Alcocoden）与寿数</div>
					{alc && alc.alcocoden ? (
						<div style={kv}>
							<span>寿主星：{sym(alc.alcocoden)}</span>
							<span>经由：{DIGNITY_CN[alc.viaDignity] || alc.viaDignity || '-'}</span>
							<span>与生命主：{alc.aspectToHyleg || '-'}</span>
							<span>宫位：{houseText(alc.house)}（{alc.angularity === 'angular' ? '角宫' : alc.angularity === 'succedent' ? '续宫' : '果宫'}）</span>
							<span>寿数档：{BAND_CN[alc.band] || alc.band}（基础 {alc.baseYears} 年）</span>
							{(alc.modifiers || []).map((m, i) => (
								<span key={i} style={{ color: m.kind === 'malefic' ? '#c0392b' : (m.kind === 'benefic' ? '#27ae60' : 'inherit') }}>
									{sym(m.planet)}{m.aspect}{m.delta > 0 ? '+' : ''}{m.delta}
								</span>
							))}
							<span style={{ fontWeight: 700 }}>预测寿数 ≈ {alc.predictedYears} 年</span>
						</div>
					) : (
						<div style={{ fontSize: 12, opacity: 0.7 }}>未能确定寿主星（生命主无具尊贵且相照之星）。</div>
					)}
				</div>

				{/* 盘主体系 */}
				<div style={cardStyle}>
					<div style={sectionTitle}>盘主体系（占控 / 家主 / 盘主）</div>
					{res.rulers ? (
						<div style={kv}>
							<span>占控星 Epikratetor：{sym(res.rulers.epikratetor)}</span>
							<span>家主星 Oikodespotes（船主）：{res.rulers.oikodespotes ? sym(res.rulers.oikodespotes) : '-'}</span>
							<span>盘主星 Kurios（舵手）：{res.rulers.kurios ? sym(res.rulers.kurios) : '-'}</span>
							{res.rulers.concordant ? <span style={{ color: '#27ae60' }}>家主=盘主，格局相合</span> : null}
						</div>
					) : <span style={{ fontSize: 12, opacity: 0.7 }}>-</span>}
				</div>

				{/* 行星状态盘 */}
				<div style={cardStyle}>
					<div style={sectionTitle}>行星状态盘</div>
					<SmallTable
						rowKey={(r) => r.planet}
						rows={res.states.rows}
						columns={[
							{ key: 'planet', title: '行星', render: (v) => sym(v) },
							{ key: 'hayyiz', title: '得时', render: (v) => (HAYYIZ_CN[v] || '—') },
							{ key: 'sunState', title: '日下', render: (v) => (SUNSTATE_CN[v] || '—') },
							{ key: 'orient', title: '出没', render: (v) => (ORIENT_CN[v] || '—') },
							{ key: 'motion', title: '行度', render: (v) => (v === 'retro' ? '逆' : '顺') },
							{ key: 'inSect', title: '同区分', render: (v) => (v ? '✓' : '—') },
							{ key: 'house', title: '宫', render: (v) => houseText(v) },
						]}
					/>
				</div>

				{/* 医疗危机 */}
				<div style={cardStyle}>
					<div style={sectionTitle}>医疗危机（Zoller 法 v1）</div>
					<div style={kv}>
						<span>第六宫：{res.medical.sixthSign ? sn(res.medical.sixthSign) : '-'}</span>
						<span>六宫主：{res.medical.sixthRuler ? sym(res.medical.sixthRuler) : '-'}</span>
						<span>生命主受克：{(res.medical.hylegAfflictions && res.medical.hylegAfflictions.length)
							? res.medical.hylegAfflictions.map((a, i) => <span key={i} style={{ color: '#c0392b', marginRight: 6 }}>{sym(a.planet)}{a.aspect}</span>)
							: '无'}</span>
						{res.medical.bodyHyleg ? <span>生命主部位：{res.medical.bodyHyleg.join('、')}</span> : null}
					</div>
					<div style={{ fontSize: 11, opacity: 0.6, marginTop: 6 }}>{res.medical.note}</div>
				</div>
			</div>
		);
	}
}

export default AstroLifespan;
