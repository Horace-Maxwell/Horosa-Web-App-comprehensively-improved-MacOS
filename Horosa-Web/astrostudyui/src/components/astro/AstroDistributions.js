// components/astro/AstroDistributions.js
// 界推运（Distributions）：上升点经主限运动穿越各埃及界 → 分配星(界主)+参与星。后端 /predict/dist。
import { Component } from 'react';
import { Spin } from 'antd';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { unwrapResult, astroSymbol, chartParams, chartRequestKey, cardStyle, SmallTable } from './AstroExtraCommon';
import * as AstroText from '../../constants/AstroText';

// AI 快照用中文名(astroSymbol 的字形在纯文本里不可读)。
function distName(id){
	if(id === undefined || id === null || id === ''){ return '-'; }
	return AstroText.AstroTxtMsg[id] || `${id}`;
}

// 界推运 AI 快照(无头):内部 fetch /predict/dist,与组件同口径。aiAnalysisContext 复算用。
export async function buildDistributionsSnapshotText(chartObj){
	if(!chartObj){ return ''; }
	let rows = [];
	try{
		const data = await request(`${Constants.ServerRoot}/predict/dist`, {
			body: JSON.stringify({ ...chartParams(chartObj) }),
			timeoutMs: 60000,
		});
		const r = unwrapResult(data) || {};
		rows = r.dist || [];
	}catch(e){
		return '';
	}
	if(!rows.length){ return ''; }  // 无界推运数据=该技法在本盘缺失,挂载显示「缺失」而非空表头。
	const lines = [];
	lines.push('[界推运（分配法 / Distributions）]');
	lines.push('上升点经主限运动穿越各埃及界；分配星=界主星，参与星=该期间内上升点触及的行星。');
	lines.push('');
	lines.push('| 分配星 | 界(座) | 参与星 | 起 | 止 |');
	lines.push('| --- | --- | --- | --- | --- |');
	rows.forEach((row)=>{
		const participants = (row.participants && row.participants.length)
			? row.participants.map(distName).join('、')
			: '—';
		lines.push(`| ${distName(row.distributor)} | ${distName(row.sign)} | ${participants} | ${row.startDate || '-'} | ${row.endDate || '-'} |`);
	});
	return lines.join('\n');
}

class AstroDistributions extends Component {
	constructor(props){
		super(props);
		this.state = { loading: false, result: null, requestKey: '' };
		this.load = this.load.bind(this);
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);
	}

	componentDidMount(){
		this.load();
		if(typeof window !== 'undefined'){ window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest); }
	}

	componentWillUnmount(){
		if(typeof window !== 'undefined'){ window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest); }
	}

	// AI导出:在界推运 tab 导出时响应刷新事件,把快照(内部 fetch /predict/dist 后)写回 detail.snapshotText,export 轮询读取。
	handleSnapshotRefreshRequest(evt){
		if(!evt || !evt.detail || evt.detail.module !== 'distributions' || !this.props.value){ return; }
		buildDistributionsSnapshotText(this.props.value).then((txt)=>{ evt.detail.snapshotText = txt || ''; }).catch(()=>{});
	}

	componentDidUpdate(){
		const k = chartRequestKey(this.props.value, 'dist');
		if(k && k !== this.state.requestKey && !this.state.loading){ this.load(); }
	}

	ensureLoaded(){
		const k = chartRequestKey(this.props.value, 'dist');
		if(k && k !== this.state.requestKey && !this.state.loading){ setTimeout(this.load, 0); }
	}

	async load(){
		if(!this.props.value){ return; }
		const k = chartRequestKey(this.props.value, 'dist');
		this.setState({ loading: true });
		try{
			const data = await request(`${Constants.ServerRoot}/predict/dist`, {
				body: JSON.stringify({ ...chartParams(this.props.value) }),
				timeoutMs: 60000,
			});
			this.setState({ result: unwrapResult(data) || {}, loading: false, requestKey: k });
		}catch(e){
			this.setState({ loading: false, requestKey: k });
		}
	}

	render(){
		this.ensureLoaded();
		const r = this.state.result || {};
		const rows = r.dist || [];
		const height = this.props.height ? this.props.height - 20 : 700;
		const sym = (id) => astroSymbol(id);
		return (
			<Spin spinning={this.state.loading}>
				<div style={{ height, overflow: 'auto', paddingRight: 8 }}>
					<div style={cardStyle}>
						<div className="horosa-info-card-title">界推运（分配法 / Distributions）</div>
						<SmallTable
							rowKey={(row, i) => i}
							rows={rows}
							columns={[
								{ key: 'distributor', title: '分配星', render: (v) => sym(v) },
								{ key: 'sign', title: '界(座)', render: (v) => sym(v) },
								{ key: 'participants', title: '参与星', render: (v) => ((v && v.length) ? v.map((p, i) => <span key={i} style={{ marginRight: 4 }}>{sym(p)}</span>) : '—') },
								{ key: 'startDate', title: '起', render: (v) => v || '-' },
								{ key: 'endDate', title: '止', render: (v) => v || '-' },
							]}
						/>
						<div style={{ fontSize: 11, opacity: 0.6, marginTop: 6 }}>上升点经主限运动穿越各埃及界；分配星=界主星，参与星=该期间内上升点触及的行星。</div>
					</div>
				</div>
			</Spin>
		);
	}
}

export default AstroDistributions;
