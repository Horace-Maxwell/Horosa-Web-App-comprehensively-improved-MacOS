import { Component } from 'react';
import { Spin, Select } from 'antd';
import { XQButton as Button, XQTabs as Tabs } from '../xq-ui';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { unwrapResult, fmtNum, chartParams, chartRequestKey, cardStyle, parkLoadFailure, clearLoadFailure, loadParked } from './AstroExtraCommon';
import ProgMethodPanel, { MINOR_VARIANT_OPTIONS } from './AstroProgChart';
import { buildTropicalProgSnapshotText } from './astroProgSnapshot';
import { DIRECTION_PAGE_SETTINGS } from '../../utils/directionPageSettings';

const TabPane = Tabs.TabPane;
const { Option } = Select;

function today(){
	const dt = new Date();
	return `${dt.getFullYear()}-${`${dt.getMonth() + 1}`.padStart(2, '0')}-${`${dt.getDate()}`.padStart(2, '0')}`;
}

function methodTab(method){
	return method.method === 'secondary' ? '二次推运' : (method.method === 'tertiary' ? '三次推运' : '小推运');
}

// 推运（回归黄道）：二次/三次/小推运。每个子 tab → 左固定推运双盘 + 右可滚动行星位置/相位表（ProgMethodPanel）。
// 小推运月长算法用顶栏「月长算法」选择器（minorVariant），缺省 synodic=标准朔望月([Q-180])。
class AstroProgressions extends Component{
	constructor(props){
		super(props);
		this.state = {
			targetDate: today(),
			targetTime: '12:00:00',
			minorVariant: DIRECTION_PAGE_SETTINGS.load().minorVariant,   // 上次亲手设的月长算法(三个推运页共用;没存过 = synodic)
			loading: false,
			result: null,
			requestKey: '',
		};
		this.load = this.load.bind(this);
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);
	}

	componentDidMount(){
		this._mounted = true;
		this.load();
		if(typeof window !== 'undefined'){
			window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}
	componentWillUnmount(){
		this._mounted = false;
		if(typeof window !== 'undefined'){
			window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}

	// [挂载自检 F-13] AI 导出刷新事件:此前本组件无监听 → 星运页导出「二次推运」经 extractSimpleModuleContent 读缓存槽
	// 'prog'(只由 AI 挂载无头重算写、任意盘)→ 导出到别人的推运;从未挂载则「无可导出文本」。按页面当前目标时刻/月长算法出。
	handleSnapshotRefreshRequest(evt){
		if(!evt || !evt.detail || evt.detail.module !== 'prog' || !this.props.value){ return; }
		buildTropicalProgSnapshotText(this.props.value, { targetDate: this.state.targetDate, targetTime: this.state.targetTime, minorVariant: this.state.minorVariant })
			.then((txt)=>{ evt.detail.snapshotText = txt || ''; }).catch(()=>{});
	}

	componentDidUpdate(){
		const key = chartRequestKey(this.props.value, `progressions|${this.state.targetDate}|${this.state.targetTime}|${this.state.minorVariant}`);
		if(key && key !== this.state.requestKey && !this.state.loading && !loadParked(this, key)){ this.load(); }
	}

	ensureLoaded(){
		const key = chartRequestKey(this.props.value, `progressions|${this.state.targetDate}|${this.state.targetTime}|${this.state.minorVariant}`);
		if(key && key !== this.state.requestKey && !this.state.loading && !loadParked(this, key)){ setTimeout(this.load, 0); }
	}

	async load(){
		if(!this.props.value){ return; }
		const key = chartRequestKey(this.props.value, `progressions|${this.state.targetDate}|${this.state.targetTime}|${this.state.minorVariant}`);
		this.setState({ loading: true });
		try{
			const data = await request(`${Constants.ServerRoot}/astroextra/progressions`, {
				body: JSON.stringify({
					...chartParams(this.props.value),
					targetDate: this.state.targetDate,
					targetTime: this.state.targetTime,
					minorVariant: this.state.minorVariant,
					orb: 1.5,
				}),
				timeoutMs: 45000,
			});
			if(!this._mounted) return;
			clearLoadFailure(this);
			this.setState({ result: unwrapResult(data) || {}, loading: false, requestKey: key });
		}catch(e){
			// 失败不把 key 记成已完成(改日期失败=永远没反应);泊车该 key,窗口期后自动重试。
			parkLoadFailure(this, key);
			if(!this._mounted) return;
			this.setState({ loading: false });
		}
	}

	render(){
		this.ensureLoaded();
		const result = this.state.result || {};
		const height = this.props.height || 700;
		// [双滚动条根治 2026-09-18] 面板高不再用「工作区高−常数」估算(常数与真实工具条/页签高不等 → 多出的十几像素把外层面板撑出第二条滚动条);
		// 内层 Tabs 走定高链(app.less .horosa-direction-page .ant-tabs-top …),面板 100% 跟随容器,任何缩放/字号/窗高零常数。
		const panelH = '100%';
		return (
			<Spin spinning={this.state.loading}>
				<div style={{ height, display: 'flex', flexDirection: 'column' }}>
					<div style={{ ...cardStyle, display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center', flex: '0 0 auto' }}>
						<label>目标日期 <input type="date" value={this.state.targetDate} onChange={(e)=>this.setState({ targetDate: e.target.value })} /></label>
						<label>时间 <input type="time" step="1" value={this.state.targetTime} onChange={(e)=>this.setState({ targetTime: e.target.value })} /></label>
						<label>月长算法 <Select size="small" style={{ width: 150 }} value={this.state.minorVariant} onChange={(v)=>{ DIRECTION_PAGE_SETTINGS.save({ minorVariant: v }); this.setState({ minorVariant: v }); }}>
							{MINOR_VARIANT_OPTIONS.map((o)=>(<Option key={o.value} value={o.value}>{o.label}</Option>))}
						</Select></label>
						<Button size="small" onClick={this.load}>计算推运</Button>
						<span>年龄天数：{fmtNum(result.ageDays, 1)}</span>
					</div>
					<Tabs defaultActiveKey="secondary" tabPosition="top" style={{ flex: '1 1 auto', minHeight: 0 }}>
						{(result.methods || []).map((method)=>(
							<TabPane tab={methodTab(method)} key={method.method}>
								<ProgMethodPanel
									value={this.props.value}
									method={method}
									targetDate={this.state.targetDate}
									targetTime={this.state.targetTime}
									mode="tropical"
									height={panelH}
									chartDisplay={this.props.chartDisplay}
									planetDisplay={this.props.planetDisplay}
									lotsDisplay={this.props.lotsDisplay}
									showAstroMeaning={this.props.showAstroMeaning}
								/>
							</TabPane>
						))}
					</Tabs>
				</div>
			</Spin>
		);
	}
}

export default AstroProgressions;
