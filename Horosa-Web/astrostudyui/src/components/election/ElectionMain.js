import { Component } from 'react';
import { Modal } from 'antd';
import { XQSelect, XQButton } from '../xq-ui';
import DivinationChartShell from '../divination/DivinationChartShell';
import ElectionJudgment from './ElectionJudgment';
import { fetchChart } from '../../services/astro';
import { buildChartParams } from '../../divination/engine/chartRequest';
import { runElection } from '../../divination/election/electionEngine';
import { generateCandidates, rankResults, buildScanRecommendation } from '../../divination/election/workflow';

const Option = XQSelect.Option;

export const ELECTION_TOPICS = [
	{ value: 'marriage', label: '结婚 / 订婚' },
	{ value: 'business', label: '创业 / 开业 / 开市' },
	{ value: 'organization', label: '团体组织成立' },
	{ value: 'move_in', label: '入宅 / 迁居' },
	{ value: 'buy_property', label: '购屋 / 租屋' },
	{ value: 'buy_land', label: '购地' },
	{ value: 'renovation', label: '整修 / 动土 / 破土' },
	{ value: 'trade', label: '买卖交易' },
	{ value: 'buy_car', label: '购车 / 交车' },
	{ value: 'contract', label: '签约 / 承诺' },
	{ value: 'registration', label: '登记 / 申请' },
	{ value: 'diet', label: '节食 / 戒习惯' },
	{ value: 'pursue_love', label: '追求爱情 / 求职' },
	{ value: 'team_departure', label: '队伍出发 / 比赛' },
	{ value: 'surgery', label: '手术 / 用药' },
	{ value: 'banquet', label: '宴会 / 就职典礼' },
	{ value: 'travel', label: '出行' },
	{ value: 'blessing', label: '祈福 / 安香 / 法会' },
	{ value: 'general_day', label: '大众吉日' },
];

const GRADE_DOT = { 极佳: '#2f9e6f', 不错: '#1aa3b8', 中等: '#3b82f6', 欠佳: '#e07a3b', '不宜（含红线）': '#cf3b3b' };

class ElectionMain extends Component{
	constructor(props){
		super(props);
		this.state = { scanning: false, scanResults: null, scanOpen: false, scanMode: 'hours' };
		this._fields = null; this._setTime = null; this._topicId = 'marriage';
		this.runScan = this.runScan.bind(this);
		this.useCandidate = this.useCandidate.bind(this);
	}

	runScan(mode){
		const baseDt = this._fields && this._fields.date && this._fields.date.value;
		if(!baseDt){ return; }
		const cands = generateCandidates(baseDt, mode, mode === 'hours' ? { startHour: 6, endHour: 22 } : { days: 14 });
		this.setState({ scanning: true, scanOpen: true, scanResults: null, scanMode: mode });
		const topicId = this._topicId;
		Promise.all(cands.map((c) => {
			const f = {
				...this._fields,
				date: { value: c.dt, name: ['date'] },
				time: { value: c.dt.clone ? c.dt.clone() : c.dt, name: ['time'] },
				ad: { value: c.dt.ad, name: ['ad'] },
				zone: { value: c.dt.zone, name: ['zone'] },
			};
			return fetchChart(buildChartParams(f), { cache: true }).then((rsp) => {
				const R = rsp && rsp.Result;
				if(!R) return null;
				const rep = runElection(R, topicId);
				return {
					label: c.label, dt: c.dt, idx: c.idx,
					score: rep.overall.score, grade: rep.overall.gradeCn,
					crit: rep.hard_flags.filter((x) => x.severity === 'critical').length,
					high: rep.hard_flags.filter((x) => x.severity === 'high').length,
				};
			}).catch(() => null);
		})).then((rows) => {
			this.setState({ scanning: false, scanResults: rankResults(rows) });
		});
	}

	useCandidate(dt){
		if(this._setTime){ this._setTime(dt); }
		this.setState({ scanOpen: false });
	}

	renderLeftExtra({ extra, setExtra, fields, setTime }){
		this._fields = fields; this._setTime = setTime; this._topicId = extra.topicId || 'marriage';
		return (
			<div className="horosa-field-block">
				<div className="horosa-field-label">用事类型</div>
				<XQSelect style={{ width: '100%' }} size="small"
					value={extra.topicId || 'marriage'}
					onChange={(val) => setExtra({ topicId: val })}>
					{ELECTION_TOPICS.map((t) => (<Option key={t.value} value={t.value}>{t.label}</Option>))}
				</XQSelect>
				<div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
					<XQButton size="small" iconName="search" onClick={() => this.runScan('hours')}>本日逐时择优</XQButton>
					<XQButton size="small" onClick={() => this.runScan('days')}>未来14日</XQButton>
				</div>
			</div>
		);
	}

	renderRight({ chart, extra }){
		return <ElectionJudgment chart={chart} topicId={extra.topicId || 'marriage'} />;
	}

	renderScanModal(){
		const r = this.state.scanResults;
		return (
			<Modal
				title={this.state.scanMode === 'hours' ? '本日逐时择优（6:00–22:00）' : '未来 14 日同时刻择优'}
				open={this.state.scanOpen}
				onCancel={() => this.setState({ scanOpen: false })}
				footer={null}
				width={460}
			>
				{this.state.scanning ? <div style={{ padding: 20, textAlign: 'center', opacity: 0.7 }}>逐一排盘评分中…</div> : null}
				{r && r.length ? (
					<div>
						<div className="horosa-divi-note" style={{ marginBottom: 10 }}>{buildScanRecommendation(r)}「没有完美的择日盘」——以下为窗口内消去法排名，分高者先。</div>
						{r.map((row, i) => (
							<div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '7px 4px', borderBottom: '1px dashed rgba(148,163,184,.2)' }}>
								<span style={{ width: 18, textAlign: 'right', opacity: 0.5, fontSize: 12 }}>{i + 1}</span>
								<span style={{ width: 78, fontWeight: 600 }}>{row.label}</span>
								<span style={{ width: 8, height: 8, borderRadius: 4, background: GRADE_DOT[row.grade] || '#888', flexShrink: 0 }} />
								<span style={{ width: 40 }}>{row.score}</span>
								<span style={{ flex: 1, fontSize: 12, opacity: 0.8 }}>{row.grade}{row.crit ? ` · 严重${row.crit}` : (row.high ? ` · 较重${row.high}` : '')}</span>
								<XQButton size="small" onClick={() => this.useCandidate(row.dt)}>用此刻</XQButton>
							</div>
						))}
					</div>
				) : (this.state.scanning ? null : <div style={{ padding: 16, opacity: 0.6 }}>无候选结果。</div>)}
			</Modal>
		);
	}

	render(){
		return (
			<div style={{ height: '100%', flex: '1 1 auto', minWidth: 0, width: '100%' }}>
				<DivinationChartShell
					title="择日盘"
					kicker="择日设置"
					pageClass="horosa-election-page"
					defaults={{ tradition: 1, zodiacal: 0, hsys: 0 }}
					initialExtra={{ topicId: 'marriage' }}
					fields={this.props.fields}
					height={this.props.height}
					chartDisplay={this.props.chartDisplay}
					planetDisplay={this.props.planetDisplay}
					lotsDisplay={this.props.lotsDisplay}
					showAstroMeaning={this.props.showAstroMeaning}
					dispatch={this.props.dispatch}
					saveModule="election"
					renderLeftExtra={(args) => this.renderLeftExtra(args)}
					renderRight={(args) => this.renderRight(args)}
				/>
				{this.renderScanModal()}
			</div>
		);
	}
}

export default ElectionMain;
