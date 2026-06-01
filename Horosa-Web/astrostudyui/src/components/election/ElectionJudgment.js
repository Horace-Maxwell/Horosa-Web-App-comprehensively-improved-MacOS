import { Component } from 'react';
import { XQTabs } from '../xq-ui';
import { runElection } from '../../divination/election/electionEngine';
import { buildElectionSnapshot } from '../../divination/election/electionSnapshot';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import { aspectsOf } from '../../divination/engine/aspectsEngine';
import { PLANETS } from '../../divination/data/planets';

const TabPane = XQTabs.TabPane;
let _lastElectionSnap = '';
function cn(k){ return (PLANETS[k] || {}).cn || k; }
const ASPECT_CN = { 0: '合相', 60: '六合', 90: '四分(刑)', 120: '三合', 180: '对分(冲)' };
const PTOLEMAIC = [0, 60, 90, 120, 180];

const SEV = {
	critical: { cn: '严重·红线', cls: 'sev-critical' },
	high: { cn: '较重', cls: 'sev-high' },
	medium: { cn: '中等', cls: 'sev-medium' },
	low: { cn: '轻微', cls: 'sev-low' },
};
const VERD = { good: { cn: '吉', color: '#2f9e6f' }, neutral: { cn: '平', color: '#3b82f6' }, caution: { cn: '留意', color: '#d2a01f' }, bad: { cn: '凶', color: '#cf5b45' } };
const GRADE = {
	excellent: { cn: '极佳', color: '#2f9e6f', desc: '窗口内难得的好时刻。' },
	good: { cn: '不错', color: '#1aa3b8', desc: '吉多于凶，可用。' },
	fair: { cn: '中等', color: '#3b82f6', desc: '吉凶参半，可再优化。' },
	poor: { cn: '欠佳', color: '#e07a3b', desc: '凶多于吉，建议换时刻。' },
	disqualified: { cn: '不宜（含红线）', color: '#cf3b3b', desc: '命中硬伤，强烈建议另择时刻。' },
};
function lineCls(pol){ return 'horosa-divi-testi' + (pol === 'positive' ? ' is-pos' : (pol === 'negative' ? ' is-neg' : '')); }
function barColor(verdict){ return (VERD[verdict] || VERD.neutral).color; }

class ElectionJudgment extends Component{
	componentDidMount(){ this.saveSnap(); }
	componentDidUpdate(){ this.saveSnap(); }
	saveSnap(){
		if(!this._j) return;
		try{ const t = buildElectionSnapshot(this._j); if(t && t !== _lastElectionSnap){ _lastElectionSnap = t; saveModuleAISnapshot('election', t, {}); } }catch(e){ /* noop */ }
	}
	render(){
		const { chart, topicId } = this.props;
		let j = null; let err = null;
		try{ j = chart ? runElection(chart, topicId) : null; }catch(e){ err = e; console.error('runElection failed', e); }
		this._j = j;
		if(!chart) return <div className="horosa-divi-judge"><div className="horosa-divi-note">排盘中…</div></div>;
		if(err || !j) return <div className="horosa-divi-judge"><div className="horosa-divi-note">判断生成失败：{String((err && err.message) || err || '无结果')}</div></div>;

		const o = j.overall;
		const g = GRADE[o.grade] || GRADE.fair;
		const moonApply = (j.facts && aspectsOf(j.facts, 'moon').filter((a) => a.applying && PTOLEMAIC.indexOf(a.angle) >= 0)) || [];
		const critCount = j.hard_flags.filter((f) => f.severity === 'critical').length;
		const highCount = j.hard_flags.filter((f) => f.severity === 'high').length;
		const tp = j.topicPack;

		return (
			<XQTabs defaultActiveKey="overall" className="horosa-inspector-tabs horosa-content-tabs">
				<TabPane tab="总评" key="overall">
					<div className="horosa-divi-judge">
						<div className="horosa-divi-card">
							<div className="horosa-divi-banner">
								<span className="horosa-divi-score" style={{ color: g.color }}>{o.score}<small> /100</small></span>
								<span className="horosa-divi-sev" style={{ background: g.color, minWidth: 64, fontSize: 12, padding: '2px 10px' }}>{g.cn}</span>
							</div>
							<div className="horosa-divi-kv" style={{ opacity: 0.8 }}>{g.desc}</div>
							<div className="horosa-divi-kv" style={{ marginTop: 4 }}>{o.headline}</div>
							{(critCount || highCount) ? <div className="horosa-divi-kv" style={{ marginTop: 2 }}>红线命中：{critCount ? `严重 ${critCount} 项` : ''}{critCount && highCount ? '、' : ''}{highCount ? `较重 ${highCount} 项` : ''}（详见「红线」页）</div> : null}
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">起盘时刻（哪一刻 ＝ 这张盘）</div>
							<div className="horosa-divi-line">{j.castMoment}</div>
						</div>
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">各分项评分（满分 100）</div>
							{j.sections.map((s) => (
								<div key={s.key} className="horosa-divi-barrow">
									<span className="lbl">{s.title}</span>
									<span className="horosa-divi-bar"><i style={{ width: s.score + '%', background: barColor(s.verdict) }} /></span>
									<span className="num">{s.score}</span>
								</div>
							))}
						</div>
						<div className="horosa-divi-note">{o.no_perfect_chart_note}</div>
					</div>
				</TabPane>

				<TabPane tab="红线" key="flags">
					<div className="horosa-divi-judge">
						<div className="horosa-divi-legend">
							「红线」＝ 对本用事的硬伤。<b style={{ color: '#cf3b3b' }}>严重</b>＝几乎应避开或换时辰；<b style={{ color: '#e07a3b' }}>较重</b>＝明显代价；<b style={{ color: '#d2a01f' }}>中等</b>/<b style={{ color: '#93a1b0' }}>轻微</b>＝小瑕疵。命中越多越重，分数越低。
						</div>
						<div className="horosa-divi-card">
							{j.hard_flags.length === 0
								? <div className="horosa-divi-testi is-pos"><span className="dot">✓</span><span>未命中任何红线，无明显硬伤。</span></div>
								: j.hard_flags.map((f, i) => {
									const sev = SEV[f.severity] || SEV.low;
									return (
										<div key={i} className="horosa-divi-flag">
											<span className={'horosa-divi-sev ' + sev.cls}>{sev.cn}</span>
											<span className="msg">{f.message}</span>
										</div>
									);
								})}
						</div>
					</div>
				</TabPane>

				<TabPane tab="分项" key="sections">
					<div className="horosa-divi-judge">
						<div className="horosa-divi-legend">按择日优先级排序：月亮 ＞ 命主星 ＞ 命度 ＞ 徵象星 ＞ 角宫… 每项满分 100。</div>
						{j.sections.map((s) => {
							const verd = VERD[s.verdict] || VERD.neutral;
							return (
								<div key={s.key} className="horosa-divi-card">
									<div className="horosa-divi-card-head">{s.title} <span className="horosa-divi-sev" style={{ background: verd.color, minWidth: 34 }}>{verd.cn}</span> <span style={{ opacity: 0.55, fontWeight: 400 }}>{s.score}/100</span></div>
									{s.findings.length ? s.findings.map((f, i) => <div key={i} className={lineCls(f.polarity)}><span className="dot">{f.polarity === 'positive' ? '▲' : (f.polarity === 'negative' ? '▼' : '·')}</span><span>{f.text_zh || f.message}</span></div>) : <div className="horosa-divi-line">无特别证词，状态平平。</div>}
									{s.detail_md ? <div className="horosa-divi-muted">{s.detail_md}</div> : null}
								</div>
							);
						})}
						{tp ? (
							<div className="horosa-divi-card">
								<div className="horosa-divi-card-head">用事专属条件（{j.topic.cn}） <span style={{ opacity: 0.55, fontWeight: 400 }}>满足 {tp.passed}/{tp.total}</span></div>
								{tp.items.length ? tp.items.map((it, i) => (
									<div key={'tp' + i} className={'horosa-divi-testi ' + (it.pass ? 'is-pos' : 'is-neg')}>
										<span className="dot">{it.pass ? '✓' : '✗'}</span>
										<span><b>{it.kind === 'avoid' ? '忌' : '宜'}</b>：{it.label}</span>
									</div>
								)) : <div className="horosa-divi-line">本用事暂无可量化的专属条件。</div>}
								{tp.notes ? <div className="horosa-divi-note">{tp.notes}</div> : null}
							</div>
						) : null}
					</div>
				</TabPane>

				<TabPane tab="应期" key="timing">
					<div className="horosa-divi-judge">
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">月亮入相位（应期：约 1°≈1 时间单位）</div>
							{moonApply.length ? moonApply.map((a, i) => <div key={i} className="horosa-divi-testi"><span className="dot">·</span><span>月 → {cn(a.other)} {ASPECT_CN[a.angle] || a.angle + '°'}（尚差 {a.orb.toFixed(1)}°）</span></div>) : <div className="horosa-divi-line">月亮无入相位（或已空亡）。</div>}
						</div>
						<div className="horosa-divi-note">把择日盘当事件本命盘：宫内星＝初期，宫主星＝后期；多个相位在同一时段成正相位 → 该期影响显著。</div>
					</div>
				</TabPane>

				<TabPane tab="建议" key="advice">
					<div className="horosa-divi-judge">
						<div className="horosa-divi-card">
							<div className="horosa-divi-card-head">建议与取舍</div>
							{j.recommendations.map((r, i) => <div key={i} className="horosa-divi-testi"><span className="dot">·</span><span>{r}</span></div>)}
						</div>
						<div className="horosa-divi-muted">消去法多候选并排比较见左栏「本日逐时择优 / 未来14日」。</div>
					</div>
				</TabPane>
			</XQTabs>
		);
	}
}

export default ElectionJudgment;
