import { Component } from 'react';
import { Spin } from 'antd';
import { XQButton as Button, XQTabs as Tabs } from '../xq-ui';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import * as AstroText from '../../constants/AstroText';
import { unwrapResult, astroSymbol, symbolWithMeaning, fmtDegree, fmtNum, chartParams, chartRequestKey, cardStyle, SmallTable } from './AstroExtraCommon';

const TabPane = Tabs.TabPane;

function today(){
	const dt = new Date();
	return `${dt.getFullYear()}-${`${dt.getMonth() + 1}`.padStart(2, '0')}-${`${dt.getDate()}`.padStart(2, '0')}`;
}

const EVENT_POINTS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Asc', 'MC'];

// 恒星推运 AI 快照（无头）：内部 fetch /astroextra/progressions + zodiacal:1，与组件同口径。无数据返回 ''。
export async function buildVedicProgSnapshotText(chartObj){
	if(!chartObj){ return ''; }
	let result = null;
	try{
		const data = await request(`${Constants.ServerRoot}/astroextra/progressions`, {
			body: JSON.stringify({
				...chartParams(chartObj),
				zodiacal: 1,
				targetDate: today(),
				targetTime: '12:00:00',
				orb: 1.5,
			}),
			timeoutMs: 45000,
		});
		result = unwrapResult(data) || {};
	}catch(e){
		return '';
	}
	const methods = (result && Array.isArray(result.methods)) ? result.methods : [];
	const secondary = methods.find((m) => m.method === 'secondary') || methods[0];
	if(!secondary || !Array.isArray(secondary.positions) || secondary.positions.length === 0){ return ''; }
	const sym = (id) => (AstroText.AstroTxtMsg[id] || `${id}`);
	const lines = [];
	lines.push('[恒星推运（Vedic Sidereal）]');
	lines.push('二次/三次/小限推运在恒星黄道（sidereal）下计算；下表为二次推运（截至今日）。');
	lines.push('');
	lines.push('| 点 | 恒星推运位置 |');
	lines.push('| --- | --- |');
	secondary.positions.filter((p) => EVENT_POINTS.indexOf(p.id) >= 0).forEach((p) => {
		lines.push(`| ${sym(p.id)} | ${fmtDegree(p)} |`);
	});
	return lines.join('\n');
}

class AstroVedicProgressions extends Component{
	constructor(props){
		super(props);
		this.state = {
			targetDate: today(),
			targetTime: '12:00:00',
			loading: false,
			result: null,
			requestKey: '',
		};
		this.load = this.load.bind(this);
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);
	}

	componentDidMount(){
		this.load();
		if(typeof window !== 'undefined'){
			window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}

	componentWillUnmount(){
		if(typeof window !== 'undefined'){
			window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}

	componentDidUpdate(){
		const key = chartRequestKey(this.props.value, `vedicprog|${this.state.targetDate}|${this.state.targetTime}`);
		if(key && key !== this.state.requestKey && !this.state.loading){
			this.load();
		}
	}

	handleSnapshotRefreshRequest(evt){
		if(!evt || !evt.detail || evt.detail.module !== 'vedicprog' || !this.props.value){ return; }
		buildVedicProgSnapshotText(this.props.value).then((txt) => { evt.detail.snapshotText = txt || ''; }).catch(() => {});
	}

	ensureLoaded(){
		const key = chartRequestKey(this.props.value, `vedicprog|${this.state.targetDate}|${this.state.targetTime}`);
		if(key && key !== this.state.requestKey && !this.state.loading){
			setTimeout(this.load, 0);
		}
	}

	async load(){
		if(!this.props.value){ return; }
		const key = chartRequestKey(this.props.value, `vedicprog|${this.state.targetDate}|${this.state.targetTime}`);
		this.setState({ loading: true });
		try{
			const data = await request(`${Constants.ServerRoot}/astroextra/progressions`, {
				body: JSON.stringify({
					...chartParams(this.props.value),
					zodiacal: 1,
					targetDate: this.state.targetDate,
					targetTime: this.state.targetTime,
					orb: 1.5,
				}),
				timeoutMs: 45000,
			});
			const result = unwrapResult(data) || {};
			this.setState({ result, loading: false, requestKey: key });
		}catch(e){
			this.setState({ loading: false, requestKey: key });
		}
	}

	renderMethod(method){
		return (
			<div style={cardStyle}>
				<div className="horosa-info-card-title">{method.label}（恒星）：{method.progressedDate && method.progressedDate.datetime}</div>
				<SmallTable
					rows={(method.positions || []).filter((item) => EVENT_POINTS.indexOf(item.id) >= 0)}
					columns={[
						{ key: 'id', title: '点', render: (v) => symbolWithMeaning(v, this.props.showAstroMeaning) },
						{ key: 'sign', title: '恒星推运位置', render: (_v, row) => fmtDegree(row) },
						{ key: 'lonspeed', title: '速度', render: (v) => fmtNum(v, 4) },
					]}
				/>
				<div style={{ height: 12 }} />
				<SmallTable
					rows={(method.aspectsToNatal || []).slice(0, 80)}
					columns={[
						{ key: 'a', title: '推运点', render: (v) => symbolWithMeaning(v, this.props.showAstroMeaning) },
						{ key: 'aspect', title: '相位', render: (v) => `${fmtNum(v, 0)}°` },
						{ key: 'b', title: '本命点', render: (v) => symbolWithMeaning(v, this.props.showAstroMeaning) },
						{ key: 'orb', title: '误差', render: (v) => fmtNum(v, 3) },
					]}
				/>
			</div>
		);
	}

	render(){
		this.ensureLoaded();
		const result = this.state.result || {};
		return (
			<Spin spinning={this.state.loading}>
				<div style={{ height: this.props.height || 700, overflow: 'auto', paddingRight: 8 }}>
					<div style={{ ...cardStyle, display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
						<span style={{ fontWeight: 600 }}>恒星推运（Vedic / Sidereal）</span>
						<label>目标日期 <input type="date" value={this.state.targetDate} onChange={(e) => this.setState({ targetDate: e.target.value })} /></label>
						<label>时间 <input type="time" step="1" value={this.state.targetTime} onChange={(e) => this.setState({ targetTime: e.target.value })} /></label>
						<Button size="small" onClick={this.load}>计算推运</Button>
						<span>年龄天数：{fmtNum(result.ageDays, 1)}</span>
					</div>
					<Tabs defaultActiveKey="secondary" tabPosition="top">
						{(result.methods || []).map((method) => (
							<TabPane tab={method.method === 'secondary' ? '二次推运' : (method.method === 'tertiary' ? '三次推运' : '小推运')} key={method.method}>
								{this.renderMethod(method)}
							</TabPane>
						))}
					</Tabs>
				</div>
			</Spin>
		);
	}
}

export default AstroVedicProgressions;
