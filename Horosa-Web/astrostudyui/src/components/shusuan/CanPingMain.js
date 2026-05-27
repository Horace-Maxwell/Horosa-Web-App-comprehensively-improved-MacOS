import { Component } from 'react';
import { Empty } from 'antd';
import { XQTabs as Tabs } from '../xq-ui';
import { buildLocalBaziResult } from '../../utils/baziLunarLocal';
import { calculate as canpingCalculate, liunianSeries, buildSnapshotText } from '../../utils/canpingLocal';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';

const { TabPane } = Tabs;

function fieldVal(fields, key, fallback = '') {
	if (!fields || !fields[key] || fields[key].value === undefined || fields[key].value === null) return fallback;
	return fields[key].value;
}

// 受控：method 由上层(数算宿主)左栏「取法」提供；slot: 'center'(主信息·滑动) | 'aux'(辅助信息·卡片)。
// 四柱来自 baziLunarLocal（星阙自己的八字，不走后端）。
class CanPingMain extends Component {
	constructor(props) {
		super(props);
		this.state = { method: props.method || 'ming' };
		this.lastSnapKey = '';
	}

	componentDidMount() { this.saveSnap(); }
	componentDidUpdate() { this.saveSnap(); }

	curMethod() { return this.props.method !== undefined ? this.props.method : this.state.method; }

	getModel() {
		const f = this.props.fields || {};
		const dateMoment = f.date && f.date.value ? f.date.value : null;
		const timeMoment = f.time && f.time.value ? f.time.value : null;
		if (!dateMoment || !timeMoment) return null;
		const dateStr = dateMoment.format('YYYY-MM-DD');
		const params = {
			date: dateStr,
			time: timeMoment.format('HH:mm:ss'),
			lon: fieldVal(f, 'lon', ''),
			gender: fieldVal(f, 'gender', 1),
			timeAlg: fieldVal(f, 'timeAlg', 1),
		};
		let bazi;
		try { bazi = buildLocalBaziResult(params).bazi; } catch (e) { return null; }
		const fc = (bazi && bazi.fourColumns) || {};
		const gz = (p) => (p && (p.ganzi || p.ganZhi)) || '';
		const yearGz = gz(fc.year);
		const monthBranch = gz(fc.month).charAt(1);
		const dayBranch = gz(fc.day).charAt(1);
		const hourBranch = gz(fc.time).charAt(1);
		if (!yearGz || !monthBranch || !dayBranch || !hourBranch) return null;
		const gender = bazi.gender === 'Female' ? '女' : '男';
		const birthYear = parseInt(dateStr.slice(0, 4), 10) || 0;
		const method = this.curMethod();
		const base = { yearGz, monthBranch, dayBranch, hourBranch, gender, method, qiyunAge: 1 };
		const r = canpingCalculate(base);
		if (!r) return null;
		let series = null;
		try { series = liunianSeries({ ...base, birthYear, startAge: 1, endAge: 120 }); } catch (e) { series = null; }
		return { r, series, birthYear };
	}

	saveSnap() {
		if (this.props.slot === 'aux') return;
		const m = this.getModel();
		if (!m) return;
		const r = m.r;
		const key = `${r.fourPillars.yearGz}|${r.method}`;
		if (key === this.lastSnapKey) return;
		this.lastSnapKey = key;
		const text = buildSnapshotText(r);
		if (text) saveModuleAISnapshot('canping', text, { source: 'react', savedAt: Date.now() });
	}

	renderAux(m) {
		const r = m.r;
		const card = (title, rows) => (
			<div className="horosa-huangji-info-card" key={title}>
				<div className="horosa-huangji-info-heading">{title}</div>
				{rows.map((x, i) => (
					<div className="horosa-huangji-info-row" key={i}><span>{x[0]}</span><strong>{x[1]}</strong></div>
				))}
			</div>
		);
		return (
			<Tabs activeKey="info" tabPosition="top" className="horosa-huangji-tabs horosa-kinastro-tabs">
				<TabPane tab="命盘信息" key="info">
					<div className="horosa-canping-aux horosa-huangji-section-list">
						{card('四柱', [
							['年柱', r.fourPillars.yearGz], ['月支', r.fourPillars.monthBranch],
							['日支', r.fourPillars.dayBranch], ['时支', r.fourPillars.hourBranch],
						])}
						{card('纳音 · 取法', [
							['年纳音', `${r.element}（${r.partName}）`],
							['取法', r.method === 'gu' ? '古法（八字日支）' : '明法（月支反向）'],
							['日宫支', r.dayPalaceBranch], ['命宫', r.mingGong],
						])}
						{card('起数', [
							['顺数', r.benming.shun], ['逆数', r.benming.ni], ['子上轮', r.benming.ziRound],
							['本命数·顺', r.benming.verses.numShun], ['本命数·逆', r.benming.verses.numNi],
						])}
					</div>
				</TabPane>
			</Tabs>
		);
	}

	renderCenter(m) {
		const r = m.r;
		const bv = r.benming.verses;
		const kindLabel = r.kindMain === 'female' ? '女命' : '男命';
		const rows = (m.series && m.series.rows) || [];
		return (
			<div className="horosa-canping-center">
				<div className="horosa-canping-toolbar">
					<span className="horosa-canping-part">{r.element}（{r.partName}）· {kindLabel}</span>
					<span className="horosa-canping-sub">取法 {r.method === 'gu' ? '古法（八字日支）' : '明法（月支反向）'} · 日宫支 {r.dayPalaceBranch} · 命宫 {r.mingGong}（左栏可切换取法）</span>
				</div>

				<div className="horosa-huangji-info-card">
					<div className="horosa-huangji-info-heading">本命（{kindLabel}）</div>
					<div className="horosa-canping-verse-num">顺 {bv.numShun}</div>
					<div className="horosa-canping-verse-text">{bv.textShun || '（空条·主贫贱夭折/灾咎）'}</div>
					<div className="horosa-canping-verse-num">逆 {bv.numNi}</div>
					<div className="horosa-canping-verse-text">{bv.textNi || '（空条·主贫贱夭折/灾咎）'}</div>
				</div>

				<div className="horosa-huangji-info-card">
					<div className="horosa-huangji-info-heading">大运（歲運）· 命宫顺行</div>
					<table className="horosa-canping-table horosa-canping-dayun">
						<thead><tr><th>年龄</th><th>支</th><th>顺 · 歲運</th><th>逆 · 歲運</th></tr></thead>
						<tbody>
							{r.dayun.map((d) => (
								<tr key={d.index}>
									<td>{d.ageStart}-{d.ageEnd}</td>
									<td>{d.branch}</td>
									<td><b>{d.numShun}</b> {(d.verses || {}).textShun}</td>
									<td><b>{d.numNi}</b> {(d.verses || {}).textNi}</td>
								</tr>
							))}
						</tbody>
					</table>
				</div>

				<div className="horosa-huangji-info-card">
					<div className="horosa-huangji-info-heading">流年（歲運）· 全表 1–120 岁（太岁替日、大运替时）</div>
					{rows.length ? (
						<table className="horosa-canping-table horosa-canping-liunian">
							<thead><tr><th>岁</th><th>干支</th><th>大运</th><th>顺 · 歲運</th><th>逆 · 歲運</th></tr></thead>
							<tbody>
								{rows.map((y) => (
									<tr key={y.age}>
										<td>{y.age}</td>
										<td>{y.ganzhi}</td>
										<td>{y.dayunBranch}</td>
										<td><b>{y.verses.numShun}</b> {y.verses.textShun}</td>
										<td><b>{y.verses.numNi}</b> {y.verses.textNi}</td>
									</tr>
								))}
							</tbody>
						</table>
					) : <div className="horosa-canping-helper">需出生年份方能列全表流年。</div>}
				</div>
			</div>
		);
	}

	render() {
		const m = this.getModel();
		if (!m) {
			if (this.props.slot === 'aux') return null;
			return <div style={{ padding: 24 }}><Empty description="请先在左侧输入出生时间" /></div>;
		}
		return this.props.slot === 'aux' ? this.renderAux(m) : this.renderCenter(m);
	}
}

export default CanPingMain;
