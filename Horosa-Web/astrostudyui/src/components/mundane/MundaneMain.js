// components/mundane/MundaneMain.js
// 世俗盘 Mundane：入宫盘（四正入宫，精确入宫时刻排盘）+ 年主星 + 木土大合相纪元（时代/大三合）。
// 入宫盘：DivinationChartShell + /jieqi 精确节气种子 + /chart。大合相：/astroextra/greatconj（swisseph 精算任意年段）。
// 时代划分：木土合相每约200年轮转一象，以打头星座命名为「时代」，附主/强/落（域主/旺/陷）。
import { Component } from 'react';
import { InputNumber, Spin } from 'antd';
import { XQSelect, XQButton } from '../xq-ui';
import DivinationChartShell from '../divination/DivinationChartShell';
import DateTime from '../comp/DateTime';
import { fetchPreciseJieqiSeed } from '../../utils/preciseCalcBridge';
import { SIGNS } from '../../divination/data/signs';
import { buildFacts } from '../../divination/engine/chartFacts';
import { buildAstroSnapshotContent } from '../../utils/astroAiSnapshot';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';

const Option = XQSelect.Option;

const INGRESSES = [
	{ term: '春分', label: '春分 · 白羊入宫（年盘）', signKey: 'aries' },
	{ term: '夏至', label: '夏至 · 巨蟹入宫', signKey: 'cancer' },
	{ term: '秋分', label: '秋分 · 天秤入宫', signKey: 'libra' },
	{ term: '冬至', label: '冬至 · 摩羯入宫', signKey: 'capricorn' },
];

const SIGN_KEYS = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'];
const SEVEN = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn'];
const PLANET_CN = { sun: '太阳', moon: '月亮', mercury: '水星', venus: '金星', mars: '火星', jupiter: '木星', saturn: '土星' };
const PLANET_GLYPH = { sun: '☉', moon: '☽', mercury: '☿', venus: '♀', mars: '♂', jupiter: '♃', saturn: '♄' };
const PLANET_ZH = { sun: '日', moon: '月', mercury: '水', venus: '金', mars: '火', jupiter: '木', saturn: '土' };
const ELEMENT_COLOR = { fire: '#c0392b', earth: '#8a6d3b', air: '#2c7fb8', water: '#1a7f6b' };
const ELEMENT_BG = { fire: 'rgba(192,57,43,0.08)', earth: 'rgba(138,109,59,0.08)', air: 'rgba(44,127,184,0.08)', water: 'rgba(26,127,107,0.08)' };
const ELEMENT_CN = { fire: '火象', earth: '土象', air: '风象', water: '水象' };
const ELEMENT_SHORT = { fire: '火', earth: '土', air: '风', water: '水' };

// 一组（约60年/3次）合相的大三合相态：纯X(全本象) / 摄Y(2本1邻) / 摄大Y(1本2邻)。
function triadPhase(triad, ageEl){
	const els = triad.map((c) => (SIGNS[SIGN_KEYS[c.sign]] || {}).element);
	const match = els.filter((e) => e === ageEl).length;
	const other = els.find((e) => e && e !== ageEl) || ageEl;
	if(match >= triad.length){ return { label: '纯' + ELEMENT_SHORT[ageEl], el: ageEl }; }
	if(match >= 2){ return { label: '摄' + ELEMENT_SHORT[other], el: other }; }
	return { label: '摄大' + ELEMENT_SHORT[other], el: other };
}

// 大三合纪元（Great Mutation）打头星座序列：每约200年进一宫。年份为天文纪年（0=前1年）。
// 序列固定（射手→摩羯→水瓶→双鱼→白羊…），锚点为各次大转换之实际合相年；两端略作外推。
const AGE_EPOCHS = [
	{ y: -1199, s: 6 }, { y: -959, s: 7 },
	{ y: -720, s: 8 }, { y: -541, s: 9 }, { y: -302, s: 10 }, { y: -124, s: 11 },
	{ y: 114, s: 0 }, { y: 292, s: 1 }, { y: 411, s: 2 }, { y: 590, s: 3 },
	{ y: 769, s: 4 }, { y: 1007, s: 5 }, { y: 1186, s: 6 }, { y: 1305, s: 7 },
	{ y: 1603, s: 8 }, { y: 1842, s: 9 }, { y: 2020, s: 10 }, { y: 2259, s: 11 },
	{ y: 2497, s: 0 }, { y: 2676, s: 1 },
];

function currentYear(){
	try{ return new Date().getFullYear(); }catch(e){ return 2026; }
}

function clampYear(v, dflt){
	const n = Number(v);
	if(!Number.isFinite(n)){ return dflt; }
	return Math.max(-3000, Math.min(3000, Math.round(n)));
}

function yearLabel(y){
	return y <= 0 ? `前${1 - y}` : `${y}`;
}

function ageEpochFor(year){
	let ep = AGE_EPOCHS[0];
	for(let i = 0; i < AGE_EPOCHS.length; i++){
		if(AGE_EPOCHS[i].y <= year){ ep = AGE_EPOCHS[i]; } else { break; }
	}
	return ep;
}

// 域主/旺/陷：主=域主星，强=七政传统旺宫，落=对宫域主（陷）。
function dignities(idx){
	const s = SIGNS[SIGN_KEYS[idx]] || {};
	const ruler = s.domicile;
	const exalt = (s.exaltation && SEVEN.indexOf(s.exaltation.planet) >= 0) ? s.exaltation.planet : null;
	const detr = (SIGNS[SIGN_KEYS[(idx + 6) % 12]] || {}).domicile;
	return { ruler, exalt, detr };
}

function dignityText(d){
	const z = (p) => PLANET_ZH[p] || p;
	const parts = [];
	if(d.ruler && d.exalt && d.ruler === d.exalt){ parts.push(z(d.ruler) + '主强'); }
	else { if(d.ruler){ parts.push(z(d.ruler) + '主'); } if(d.exalt){ parts.push(z(d.exalt) + '强'); } }
	if(d.detr){ parts.push(z(d.detr) + '落'); }
	return parts.join('·');
}

// 把合相按纪元归组为「时代」。
function computeAges(conjs){
	const ages = [];
	let cur = null;
	(conjs || []).forEach((c) => {
		const ep = ageEpochFor(c.year);
		if(!cur || cur.epochY !== ep.y){
			if(cur){ ages.push(cur); }
			const sign = SIGNS[SIGN_KEYS[ep.s]] || {};
			cur = {
				epochY: ep.y, leadingCn: sign.cn, leadingGlyph: sign.glyph,
				element: sign.element, dignities: dignities(ep.s), conjs: [],
			};
		}
		cur.conjs.push(c);
	});
	if(cur){ ages.push(cur); }
	return ages;
}

// 入宫盘上升座 → 域主星 = 年主星。buildFacts 给 meta.ascSign（小写座 key）。
function ascRuler(chart){
	let key = null;
	let lon = null;
	try{
		const facts = buildFacts(chart);
		if(facts && facts.meta){
			if(facts.meta.ascSign){ key = facts.meta.ascSign; }
			else if(facts.meta.ascLon != null){ lon = facts.meta.ascLon; }
		}
		if(key == null && facts && facts.lons && facts.lons.asc != null){ lon = facts.lons.asc; }
	}catch(e){ /* noop */ }
	if(key == null && lon != null){ key = SIGN_KEYS[Math.floor((((lon % 360) + 360) % 360) / 30)]; }
	const sign = key ? SIGNS[key] : null;
	if(!sign){ return null; }
	return { signCn: sign.cn, signGlyph: sign.glyph, rulerCn: PLANET_CN[sign.domicile] || sign.domicile, rulerGlyph: PLANET_GLYPH[sign.domicile] || '' };
}

const CARD = {
	border: '1px solid var(--horosa-border, rgba(128,128,128,0.16))',
	borderRadius: 12,
	padding: '14px 16px',
	marginBottom: 14,
	background: 'var(--horosa-card-bg, rgba(128,128,128,0.025))',
};
const CARD_TITLE = { fontSize: 13.5, fontWeight: 700, marginBottom: 12, letterSpacing: '0.03em', display: 'flex', alignItems: 'center', gap: 8 };

class MundaneMain extends Component {
	constructor(props){
		super(props);
		const y = currentYear();
		this.state = {
			casting: false, err: '',
			gcStart: 1300, gcEnd: 2200, gcLoading: false, gcResults: null, gcErr: '',
		};
		this.castIngress = this.castIngress.bind(this);
		this.computeGreatConj = this.computeGreatConj.bind(this);
	}

	componentDidMount(){
		// 首次自动算一段，省一次点击；范围跨 4 个时代。
		this.computeGreatConj();
	}

	async castIngress(extra, setExtra, fields, setTime){
		const term = extra.ingressTerm || '春分';
		const year = clampYear(extra.ingressYear, currentYear());
		const zone = fields.zone ? fields.zone.value : '+08:00';
		this.setState({ casting: true, err: '' });
		try{
			const params = {
				year: String(year),
				ad: fields.ad ? fields.ad.value : 1,
				zone,
				lon: fields.lon ? fields.lon.value : '116e23',
				lat: '23n26',
				gpsLat: 23.43,
				gpsLon: fields.gpsLon ? fields.gpsLon.value : (fields.lon ? fields.lon.value : 0),
				timeAlg: 0,
				jieqis: [term],
			};
			const seed = await fetchPreciseJieqiSeed(params);
			const hit = seed && seed[term];
			if(!hit || !hit.time){ throw new Error('未取到入宫时刻'); }
			const dt = new DateTime();
			dt.parse(hit.time, 'YYYY-MM-DD HH:mm:ss');
			dt.zone = zone;
			dt.calcJdn();
			setExtra({ ingressTerm: term, ingressYear: year, ingressMoment: hit.time });
			setTime(dt);
			this.setState({ casting: false });
		}catch(e){
			this.setState({ casting: false, err: (e && e.message) || '入宫盘排盘失败' });
		}
	}

	async computeGreatConj(){
		const startYear = clampYear(this.state.gcStart, 1300);
		const endYear = clampYear(this.state.gcEnd, 2200);
		if(endYear < startYear){ this.setState({ gcErr: '结束年须不小于起始年' }); return; }
		this.setState({ gcLoading: true, gcErr: '' });
		try{
			const data = await request(`${Constants.ServerRoot}/astroextra/greatconj`, {
				body: JSON.stringify({ startYear, endYear }),
				timeoutMs: 90000,
			});
			const r = (data && data.Result) ? data.Result : data;
			const list = (r && r.conjunctions) ? r.conjunctions : (Array.isArray(r) ? r : []);
			this.setState({ gcLoading: false, gcResults: list });
		}catch(e){
			this.setState({ gcLoading: false, gcErr: '大合相计算失败' });
		}
	}

	renderLeftExtra({ extra, setExtra, fields, setTime }){
		const term = extra.ingressTerm || '春分';
		const year = extra.ingressYear != null ? extra.ingressYear : currentYear();
		return (
			<div className="horosa-field-block">
				<div className="horosa-field-label">入宫盘</div>
				<XQSelect style={{ width: '100%', marginBottom: 8 }} size="small" value={term}
					onChange={(v) => setExtra({ ingressTerm: v })}>
					{INGRESSES.map((it) => (<Option key={it.term} value={it.term}>{it.label}</Option>))}
				</XQSelect>
				<div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
					<InputNumber size="small" style={{ flex: 1 }} value={year} min={-3000} max={3000}
						onChange={(v) => setExtra({ ingressYear: clampYear(v, currentYear()) })} />
					<span style={{ fontSize: 12, opacity: 0.7 }}>年</span>
				</div>
				<XQButton size="small" style={{ width: '100%' }} disabled={this.state.casting}
					onClick={() => this.castIngress(extra, setExtra, fields, setTime)}>{this.state.casting ? '排盘中…' : '排入宫盘'}</XQButton>
				{extra.ingressMoment ? (
					<div style={{ fontSize: 11, opacity: 0.65, marginTop: 6 }}>入宫时刻：{extra.ingressMoment}</div>
				) : null}
				{this.state.err ? (
					<div style={{ fontSize: 11, color: '#c0392b', marginTop: 6 }}>{this.state.err}</div>
				) : null}
			</div>
		);
	}

	renderYearChart(chart, extra){
		const yl = chart ? ascRuler(chart) : null;
		const ing = INGRESSES.find((i) => i.term === (extra.ingressTerm || '春分'));
		return (
			<div style={CARD}>
				<div style={CARD_TITLE}><span style={{ width: 3, height: 14, background: '#b8860b', borderRadius: 2, display: 'inline-block' }} />年盘概要</div>
				{extra.ingressMoment ? (
					<div>
						<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
							<span style={{ fontSize: 16, fontWeight: 700 }}>{extra.ingressYear != null ? extra.ingressYear : currentYear()} 年</span>
							<span style={{ fontSize: 12, opacity: 0.7 }}>{ing ? ing.label.split('（')[0] : '春分入宫'}</span>
						</div>
						<div style={{ fontSize: 11.5, opacity: 0.55, marginBottom: 12 }}>入宫时刻 {extra.ingressMoment}</div>
						{yl ? (
							<div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 10, background: 'rgba(184,134,11,0.10)', border: '1px solid rgba(184,134,11,0.18)' }}>
								<div style={{ textAlign: 'center' }}>
									<div style={{ fontSize: 10, opacity: 0.6 }}>上升</div>
									<div style={{ fontSize: 20, lineHeight: '24px' }}>{yl.signGlyph}</div>
									<div style={{ fontSize: 12 }}>{yl.signCn}</div>
								</div>
								<span style={{ opacity: 0.4, fontSize: 18 }}>→</span>
								<div style={{ textAlign: 'center' }}>
									<div style={{ fontSize: 10, opacity: 0.6, color: '#b8860b' }}>年主星 · 命主</div>
									<div style={{ fontSize: 22, lineHeight: '26px', color: '#b8860b' }}>{yl.rulerGlyph}</div>
									<div style={{ fontSize: 13, fontWeight: 700, color: '#b8860b' }}>{yl.rulerCn}</div>
								</div>
							</div>
						) : null}
						<div style={{ fontSize: 11, opacity: 0.5, marginTop: 10, lineHeight: '16px' }}>年主星即入宫盘上升座之域主星，主导该年/季世俗主题；再综合四轴、十宫（政权）、各宫主星状态论断。</div>
					</div>
				) : (
					<div style={{ fontSize: 12, opacity: 0.55 }}>左栏选年份与入宫节气，点「排入宫盘」按精确入宫时刻起盘。春分白羊入宫盘 = 该年年盘。</div>
				)}
			</div>
		);
	}

	renderAge(age, i){
		const col = ELEMENT_COLOR[age.element] || '#888';
		const triads = [];
		for(let k = 0; k < age.conjs.length; k += 3){ triads.push(age.conjs.slice(k, k + 3)); }
		return (
			<div key={i} style={{ border: '1px solid rgba(128,128,128,0.14)', borderLeft: `3px solid ${col}`, borderRadius: 8, marginBottom: 10, overflow: 'hidden' }}>
				<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: ELEMENT_BG[age.element] }}>
					<div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
						<span style={{ fontSize: 17 }}>{age.leadingGlyph}</span>
						<span style={{ fontSize: 14, fontWeight: 700 }}>{age.leadingCn}时代</span>
						<span style={{ fontSize: 11, color: col, border: `1px solid ${col}`, borderRadius: 4, padding: '0 5px', opacity: 0.9 }}>{ELEMENT_CN[age.element]}</span>
					</div>
					<span style={{ fontSize: 12, fontWeight: 600, color: col }}>{dignityText(age.dignities)}</span>
				</div>
				<div style={{ padding: '4px 12px 8px' }}>
					{triads.map((triad, ti) => {
						const ph = triadPhase(triad, age.element);
						const pcol = ELEMENT_COLOR[ph.el] || col;
						return (
							<div key={ti}>
								<div style={{ fontSize: 11, color: pcol, fontWeight: 600, margin: ti ? '8px 0 2px' : '4px 0 2px', letterSpacing: '0.05em' }}>{ph.label}</div>
								{triad.map((g, j) => {
									const sg = SIGNS[SIGN_KEYS[g.sign]] || {};
									const el = sg.element || 'earth';
									const transit = el !== age.element;
									const deg = g.lon != null ? `${(g.lon % 30).toFixed(1)}°` : '';
									return (
										<div key={j} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '2.5px 0', fontSize: 12.5, borderTop: j ? '1px solid rgba(128,128,128,0.06)' : 'none' }}>
											<span style={{ width: 76, opacity: 0.65, whiteSpace: 'nowrap' }}>{yearLabel(g.year)}-{String(g.month).padStart(2, '0')}</span>
											<span style={{ flex: 1, whiteSpace: 'nowrap' }}>
												<span style={{ color: ELEMENT_COLOR[el], marginRight: 4 }}>{sg.glyph}</span>{sg.cn}
												{transit ? <span style={{ fontSize: 10, opacity: 0.45, marginLeft: 6 }}>过渡</span> : null}
											</span>
											<span style={{ width: 46, textAlign: 'right', opacity: 0.65 }}>{deg}</span>
										</div>
									);
								})}
							</div>
						);
					})}
				</div>
			</div>
		);
	}

	renderGreatConj(){
		const ages = this.state.gcResults ? computeAges(this.state.gcResults) : null;
		const total = this.state.gcResults ? this.state.gcResults.length : 0;
		return (
			<div style={CARD}>
				<div style={CARD_TITLE}><span style={{ width: 3, height: 14, background: '#2c7fb8', borderRadius: 2, display: 'inline-block' }} />木土大合相 · 时代纪元</div>
				<div style={{ fontSize: 11, opacity: 0.6, marginBottom: 10, lineHeight: '17px' }}>木土约 20 年一会、约 200 年轮转一象（大三合 Trigon）。以打头星座命名「时代」；2020 宝瓶大合相 = 由土象转风象的大转换，启约 200 年风象时代。</div>
				<div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12, flexWrap: 'wrap' }}>
					<InputNumber size="small" style={{ width: 80 }} value={this.state.gcStart} min={-3000} max={3000}
						onChange={(v) => this.setState({ gcStart: clampYear(v, 1300) })} />
					<span style={{ fontSize: 12, opacity: 0.6 }}>至</span>
					<InputNumber size="small" style={{ width: 80 }} value={this.state.gcEnd} min={-3000} max={3000}
						onChange={(v) => this.setState({ gcEnd: clampYear(v, 2200) })} />
					<XQButton size="small" disabled={this.state.gcLoading} onClick={this.computeGreatConj}>{this.state.gcLoading ? '计算中…' : '计算时代'}</XQButton>
					<span style={{ fontSize: 11, opacity: 0.45 }}>支持 前3000 – 3000</span>
				</div>
				{this.state.gcErr ? <div style={{ fontSize: 11, color: '#c0392b', marginBottom: 8 }}>{this.state.gcErr}</div> : null}
				<Spin spinning={this.state.gcLoading}>
					{ages && ages.length ? (
						<div style={{ maxHeight: 460, overflowY: 'auto', paddingRight: 4 }}>
							{ages.map((a, i) => this.renderAge(a, i))}
							<div style={{ fontSize: 11, opacity: 0.45, marginTop: 4 }}>{ages.length} 个时代 · {total} 次合相（swisseph 精算，含三重合相分列；「过渡」= 该次合相落入下一象，预示大转换）。</div>
						</div>
					) : (
						<div style={{ fontSize: 12, opacity: 0.55, padding: '6px 0' }}>设定年段后点「计算时代」，按星历精算该区间全部木土合相，并归入各时代（座 / 度 / 象 / 主强落）。</div>
					)}
				</Spin>
			</div>
		);
	}

	renderRight({ chart, extra }){
		return (
			<div style={{ fontSize: 13 }}>
				{this.renderYearChart(chart, extra)}
				{this.renderGreatConj()}
			</div>
		);
	}

	render(){
		return (
			<DivinationChartShell
				title="世俗盘"
				kicker="入宫设置"
				pageClass="horosa-mundane-page"
				castNowLabel="此刻起盘"
				defaults={{ tradition: 1, zodiacal: 0, hsys: 0 }}
				initialExtra={{ ingressTerm: '春分', ingressYear: currentYear() }}
				fields={this.props.fields}
				height={this.props.height}
				chartDisplay={this.props.chartDisplay}
				planetDisplay={this.props.planetDisplay}
				lotsDisplay={this.props.lotsDisplay}
				showAstroMeaning={this.props.showAstroMeaning}
				dispatch={this.props.dispatch}
				saveModule="mundane"
				buildAiSnapshot={(chart, fields, extra) => {
					const ex = extra || {};
					// 入宫元信息做成可被 AI导出 段筛选的 [世俗入宫] 段;正文复用本命 astro 快照(含12分度/主宰链/寿命等)。
					const head = ['[世俗入宫]', `入宫节气：${ex.ingressTerm || '-'}`, `年份：${ex.ingressYear || '-'}`].join('\n');
					const body = buildAstroSnapshotContent(chart, fields) || '';
					return [head, body].filter(Boolean).join('\n\n');
				}}
				renderLeftExtra={(args) => this.renderLeftExtra(args)}
				renderRight={(args) => this.renderRight(args)}
			/>
		);
	}
}

export default MundaneMain;
