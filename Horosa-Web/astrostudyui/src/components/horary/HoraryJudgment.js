import { Component } from 'react';
import { XQTabs } from '../xq-ui';
import { runHorary, ASPECT_CN } from '../../divination/horary/horaryEngine';
import { buildHorarySnapshot } from '../../divination/horary/horarySnapshot';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import { PLANETS } from '../../divination/data/planets';
import { SIGNS } from '../../divination/data/signs';

const TabPane = XQTabs.TabPane;
let _lastHorarySnap = '';
function cn(k){ return (PLANETS[k] || {}).cn || k || '—'; }
const ANG_CN = { angular: '角宫·有力', succedent: '续宫·中等', cadent: '果宫·偏弱' };
const LEAN = {
	yes: { word: '倾向：成', sub: '完成法命中、吉证占优 → 多向「成」倾斜。仍须结合实际，不替您下命定结论。', cls: 'lean-yes' },
	no: { word: '倾向：不成 / 受阻', sub: '完成受阻或凶证占优 → 多向「不成」倾斜。建议另择时再问。', cls: 'lean-no' },
	even: { word: '倾向：势均力敌', sub: '吉凶证词相当、未见明确完成法 → 建议换更合适的时机重新起卦。', cls: 'lean-even' },
};

function plainState(facts, k){
	const p = facts.planets[k];
	if(!p) return '';
	const sgn = (SIGNS[p.sign] || {}).cn || p.sign;
	const ang = ANG_CN[p.angularity] || '';
	const dig = p.dignityScore >= 4 ? '入庙旺·有力' : (p.dignityScore <= -4 ? '落陷失势·无力' : (p.peregrine ? '游走·无尊贵' : '尊贵平平'));
	const extra = [];
	if(p.retro) extra.push('逆行');
	if(p.combustion === 'combust') extra.push('燃烧受灼');
	else if(p.combustion === 'cazimi') extra.push('居日心·极强');
	else if(p.combustion === 'under_beams') extra.push('日光束下');
	return `落 ${sgn}座 · 第${p.house || '?'}宫 · ${ang} · ${dig}${extra.length ? ' · ' + extra.join('/') : ''}`;
}

class HoraryJudgment extends Component{
	componentDidMount(){ this.saveSnap(); }
	componentDidUpdate(){ this.saveSnap(); }
	saveSnap(){
		if(!this._j) return;
		try{ const t = buildHorarySnapshot(this._j); if(t && t !== _lastHorarySnap){ _lastHorarySnap = t; saveModuleAISnapshot('horary', t, {}); } }catch(e){ /* noop */ }
	}
	render(){
		const { chart, category } = this.props;
		let j = null; let err = null;
		try{ j = chart ? runHorary(chart, category) : null; }catch(e){ err = e; console.error('runHorary failed', e); }
		this._j = j;
		if(!chart) return <div className="horosa-divi-judge"><div className="horosa-divi-note">排盘中…</div></div>;
		if(err || !j) return <div className="horosa-divi-judge"><div className="horosa-divi-note">判断生成失败：{String((err && err.message) || err || '无结果')}</div></div>;

		const sig = j.significators;
		const rad = j.radicality;
		const perf = j.perfection;
		const v = j.verdict;
		const lean = LEAN[v.leaning] || LEAN.even;
		const facts = j.facts;
		const moonStory = j.moonStory || { separating: [], applying: [] };
		const allAspects = j.allAspects || [];

		return (
			<XQTabs defaultActiveKey="verdict" className="horosa-inspector-tabs horosa-content-tabs">
				<TabPane tab="裁决" key="verdict">
					<div className="horosa-divi-judge">
						<div className={'horosa-divi-verdict-big ' + lean.cls}>
							{lean.word}
							<div className="sub">{lean.sub}</div>
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-subhead pos">有利证词（{v.positive.length}）</div>
							{v.positive.length ? v.positive.map((p, i) => <div key={i} className="horosa-divi-testi is-pos"><span className="dot">▲</span><span>{p.text}</span></div>) : <div className="horosa-divi-line">暂无明显有利证词。</div>}
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-subhead neg">不利证词（{v.negative.length}）</div>
							{v.negative.length ? v.negative.map((n, i) => <div key={i} className="horosa-divi-testi is-neg"><span className="dot">▼</span><span>{n.text}</span></div>) : <div className="horosa-divi-line">暂无明显不利证词。</div>}
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">六类问法（Sibly Query）</div>
							<div className="horosa-divi-kv">① 能否成事：{j.queries.canHappen.text}</div>
							<div className="horosa-divi-kv">② 事情好坏：{j.queries.goodEvil.text}</div>
							<div className="horosa-divi-kv">③ 消息真假：{j.queries.reportTrue.text}</div>
						</div>
						<div className="horosa-divi-note">卜卦只呈现证据与倾向，不替您下命定结论；势均力敌时建议另择时再问。</div>
					</div>
				</TabPane>

				<TabPane tab="征象" key="sig">
					<div className="horosa-divi-judge">
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">这一盘适合判断吗？（根本性）</div>
							<div className="horosa-divi-legend">检查此盘是否真诚自然、可信地判断。有警告不代表不能判，只是提醒慎重。</div>
							{rad.suitable ? <div className="horosa-divi-testi is-pos"><span className="dot">✓</span><span>盘面端正，适合判断。</span></div> : null}
							{rad.ok.map((t, i) => <div key={'ok' + i} className="horosa-divi-testi is-pos"><span className="dot">✓</span><span>{t}</span></div>)}
							{rad.warnings.map((w, i) => <div key={'w' + i} className="horosa-divi-testi is-neg"><span className="dot">⚠</span><span>{w.text}</span></div>)}
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">谁代表谁（征象星指派）</div>
							<div className="horosa-divi-kv">问卜者本人 ＝ 命宫主星 <span className="tag">{cn(sig.querentKey)}</span> ＋ 月亮</div>
							<div className="horosa-divi-kv">{sig.quesitedLabel || '所问之事'} ＝ {sig.quesitedHouse ? sig.quesitedHouse + '宫主 ' : ''}<span className="tag">{cn(sig.quesitedKey)}</span></div>
							{sig.natural ? <div className="horosa-divi-kv">自然征象星（该事项的天然代表）＝ <span className="tag">{cn(sig.natural)}</span></div> : null}
							<div className="horosa-divi-kv">此刻「时主星」（活跃征象）＝ <span className="tag">{cn(j.hourRuler)}</span></div>
						</div>
						<div className="horosa-divi-legend">各征象星力量：入庙旺=有力；落陷/游走/燃烧/逆行=无力或受损；角宫快而有力，果宫弱而拖延。</div>
						{Object.keys(j.conditions).map((k) => {
							const c = j.conditions[k];
							const role = k === sig.querentKey ? '（问卜者）' : (k === sig.quesitedKey ? '（' + (sig.quesitedLabel || '事项') + '）' : (k === 'moon' ? '（共同征象）' : ''));
							return (
								<div key={k} className="horosa-divi-card">
									<div className="horosa-divi-card-head">{cn(k)}<span style={{ fontWeight: 400, opacity: 0.7 }}>{role}</span> <span className="horosa-divi-sev" style={{ background: c.score > 0 ? '#2f9e6f' : (c.score < 0 ? '#cf5b45' : '#93a1b0'), minWidth: 52 }}>力量 {c.score > 0 ? '+' : ''}{c.score}</span></div>
									<div className="horosa-divi-kv" style={{ opacity: 0.85 }}>{plainState(facts, k)}</div>
									{c.findings.map((f, i) => <div key={i} className={'horosa-divi-testi ' + (f.polarity === 'positive' ? 'is-pos' : (f.polarity === 'negative' ? 'is-neg' : ''))}><span className="dot">{f.polarity === 'positive' ? '▲' : (f.polarity === 'negative' ? '▼' : '·')}</span><span>{f.text_zh}</span></div>)}
								</div>
							);
						})}
					</div>
				</TabPane>

				<TabPane tab="完成" key="perfection">
					<div className="horosa-divi-judge">
						<div className="horosa-divi-legend">「完成法」＝两颗征象星怎样接通：① <b>入相位</b>（直接成相）；② <b>光线传递</b>（第三颗星先离开 A、再去接 B，当中间人）；③ <b>光线汇集</b>（两星都去接同一颗较重星）；④ <b>落位</b>。接不上 / 被抢先 / 燃烧 / 刚出相＝难成。下面把所有线索摆出，供你自行判断。</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">本盘命中的完成 / 破坏</div>
							{perf ? perf.detail.map((d, i) => <div key={i} className="horosa-divi-testi"><span className="dot">·</span><span>{d}</span></div>) : <div className="horosa-divi-line">征象星不全，无法判断完成法。</div>}
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">月亮的故事（过去 → 未来）</div>
							<div className="horosa-divi-legend">月亮刚离开的星＝事情来由/已过；接下来要会的星＝事情走向/将发生（卜卦最重要的线索之一）。</div>
							{moonStory.separating.slice(0, 2).map((a, i) => <div key={'sep' + i} className="horosa-divi-testi"><span className="dot">↤</span><span>月 刚离开 {cn(a.other)}（{ASPECT_CN[a.angle]}，已过 {a.orb.toFixed(1)}°）</span></div>)}
							{moonStory.applying.length ? moonStory.applying.slice(0, 3).map((a, i) => <div key={'app' + i} className={'horosa-divi-testi ' + (a.nature === 'positive' ? 'is-pos' : (a.nature === 'negative' ? 'is-neg' : ''))}><span className="dot">↦</span><span>月 接下来会 {cn(a.other)}（{ASPECT_CN[a.angle]}，还差 {a.orb.toFixed(1)}°）</span></div>) : <div className="horosa-divi-line">月亮接下来无主相位（空亡）。</div>}
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">相位全览（七政之间）</div>
							<div className="horosa-divi-legend">所有成相的星对，供你核对征象。<b>入相</b>＝正在靠近、主未来/将成；<b>出相</b>＝正在远离、主过去/已过。</div>
							{allAspects.length ? allAspects.map((a, i) => (
								<div key={i} className={'horosa-divi-testi ' + (a.nature === 'positive' ? 'is-pos' : (a.nature === 'negative' ? 'is-neg' : ''))}>
									<span className="dot">{a.applying ? '↦' : '↤'}</span>
									<span>{cn(a.a)} {ASPECT_CN[a.angle]} {cn(a.b)} · {a.applying ? '入相' : '出相'} · 差 {a.orb.toFixed(1)}°{a.exact ? ' · 正相位！' : ''}</span>
								</div>
							)) : <div className="horosa-divi-line">七政之间暂无成相。</div>}
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">完成度（三分法则）</div>
							<div className="horosa-divi-legend">把命主、月亮、事项星三颗当「三大征象」，数有几颗「安全」（不逆行 / 不燃烧 / 不落陷）。安全越多，越能办成。</div>
							<div className="horosa-divi-kv">安全 <b>{j.thirds.count}/{j.thirds.total}</b> → {({ all: '三颗全安全 → 大致可圆满达成', '2/3': '两颗安全 → 约完成三分之二', '1/3': '一颗安全 → 约完成三分之一', none: '皆不安全 → 难成 / 易败坏' })[j.thirds.fraction] || j.thirds.fraction}</div>
						</div>
					</div>
				</TabPane>

				<TabPane tab="时空" key="timing">
					<div className="horosa-divi-judge">
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">何时（应期）</div>
							<div className="horosa-divi-line">{j.timing ? j.timing.text : '无准确相位，应期不定（多半不成或需另择时）。'}</div>
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">何处（方位）</div>
							<div className="horosa-divi-line">{j.queries.where ? `${j.queries.where.dir}（${j.queries.where.terrain}），距离${j.queries.where.distance}` : '本问题无方位指示。'}</div>
						</div>
					</div>
				</TabPane>

				<TabPane tab="描述" key="describe">
					<div className="horosa-divi-judge">
						{(j.describe && j.describe.length) ? j.describe.map((d, i) => (
							<div key={i} className="horosa-divi-card">
								<div className="horosa-divi-card-head">{d.role}：{d.title}{d.temper ? <span style={{ fontWeight: 400, opacity: 0.7 }}>（性情{d.temper}）</span> : null}</div>
								<div className="horosa-divi-line">{d.body}</div>
							</div>
						)) : <div className="horosa-divi-note">本问题类别暂无人物/事物描述。</div>}
						{j.theft ? (
							<div className="horosa-divi-card">
								<div className="horosa-divi-card-head">盗窃 / 失物（11 步）</div>
								<div className="horosa-divi-legend">失主＝命主＋月亮；盗贼＝7宫主 <b>{cn(j.theft.thief)}</b>；赃物＝2宫主 <b>{cn(j.theft.obj)}</b>；藏匿地＝4宫。</div>
								{j.theft.steps.map((s, i) => (
									<div key={i} className={'horosa-divi-testi ' + (s.polarity === 'positive' ? 'is-pos' : (s.polarity === 'negative' ? 'is-neg' : ''))}>
										<span className="dot" style={{ fontWeight: 600 }}>{s.label}</span><span>{s.text}</span>
									</div>
								))}
							</div>
						) : null}
						<div className="horosa-divi-muted">描述取「征象星 落 星座」（Sibly 84 条）＋ 行星性情；小偷/疾病/死亡按类别叠加。</div>
					</div>
				</TabPane>
			</XQTabs>
		);
	}
}

export default HoraryJudgment;
