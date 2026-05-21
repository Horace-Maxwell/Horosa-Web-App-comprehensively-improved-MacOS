import { Component } from 'react';
import { Spin } from 'antd';
import { XQButton as Button, XQTabs as Tabs } from '../xq-ui';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { unwrapResult, astroSymbol, fmtDegree, fmtNum, chartParams, chartRequestKey, cardStyle, SmallTable } from './AstroExtraCommon';

const TabPane = Tabs.TabPane;

function today(){
	const dt = new Date();
	return `${dt.getFullYear()}-${`${dt.getMonth() + 1}`.padStart(2, '0')}-${`${dt.getDate()}`.padStart(2, '0')}`;
}

class AstroProgressions extends Component{
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
	}

	componentDidMount(){
		this.load();
	}

	componentDidUpdate(prevProps){
		const key = chartRequestKey(this.props.value, `progressions|${this.state.targetDate}|${this.state.targetTime}`);
		if(key && key !== this.state.requestKey && !this.state.loading){
			this.load();
		}
	}

	ensureLoaded(){
		const key = chartRequestKey(this.props.value, `progressions|${this.state.targetDate}|${this.state.targetTime}`);
		if(key && key !== this.state.requestKey && !this.state.loading){
			setTimeout(this.load, 0);
		}
	}

	async load(){
		if(!this.props.value){
			return;
		}
		const key = chartRequestKey(this.props.value, `progressions|${this.state.targetDate}|${this.state.targetTime}`);
		this.setState({loading: true});
		try{
			const data = await request(`${Constants.ServerRoot}/astroextra/progressions`, {
				body: JSON.stringify({
					...chartParams(this.props.value),
					targetDate: this.state.targetDate,
					targetTime: this.state.targetTime,
					orb: 1.5,
				}),
				timeoutMs: 45000,
			});
			this.setState({result: unwrapResult(data) || {}, loading: false, requestKey: key});
		}catch(e){
			this.setState({loading: false, requestKey: key});
		}
	}

	renderMethod(method){
		return (
			<div style={cardStyle}>
				<div className="horosa-info-card-title">{method.label}：{method.progressedDate && method.progressedDate.datetime}</div>
				<SmallTable
					rows={(method.positions || []).filter((item)=>['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Asc','MC'].indexOf(item.id) >= 0)}
					columns={[
						{key: 'id', title: '点', render: (v)=>astroSymbol(v)},
						{key: 'sign', title: '推运位置', render: (_v, row)=>fmtDegree(row)},
						{key: 'lonspeed', title: '速度', render: (v)=>fmtNum(v, 4)},
					]}
				/>
				<div style={{height: 12}} />
				<SmallTable
					rows={(method.aspectsToNatal || []).slice(0, 80)}
					columns={[
						{key: 'a', title: '推运点', render: (v)=>astroSymbol(v)},
						{key: 'aspect', title: '相位', render: (v)=>`${fmtNum(v, 0)}°`},
						{key: 'b', title: '本命点', render: (v)=>astroSymbol(v)},
						{key: 'orb', title: '误差', render: (v)=>fmtNum(v, 3)},
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
				<div style={{height: this.props.height || 700, overflow: 'auto', paddingRight: 8}}>
					<div style={{...cardStyle, display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center'}}>
						<label>目标日期 <input type="date" value={this.state.targetDate} onChange={(e)=>this.setState({targetDate: e.target.value})} /></label>
						<label>时间 <input type="time" step="1" value={this.state.targetTime} onChange={(e)=>this.setState({targetTime: e.target.value})} /></label>
						<Button size="small" onClick={this.load}>计算推运</Button>
						<span>年龄天数：{fmtNum(result.ageDays, 1)}</span>
					</div>
					<Tabs defaultActiveKey="secondary" tabPosition="top">
						{(result.methods || []).map((method)=>(
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

export default AstroProgressions;
