import { Component } from 'react';
import { Spin, Checkbox } from 'antd';
import { XQButton as Button, XQTabs as Tabs } from '../xq-ui';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { unwrapResult, astroSymbol, fmtDegree, fmtNum, chartParams, chartRequestKey, cardStyle, SmallTable } from './AstroExtraCommon';

const TabPane = Tabs.TabPane;

function addDays(date, days){
	const dt = new Date(date.getTime());
	dt.setDate(dt.getDate() + days);
	return dt;
}

function fmtDate(date){
	const y = date.getFullYear();
	const m = `${date.getMonth() + 1}`.padStart(2, '0');
	const d = `${date.getDate()}`.padStart(2, '0');
	return `${y}-${m}-${d}`;
}

class AstroEphemeris extends Component{
	constructor(props){
		super(props);
		const now = new Date();
		this.state = {
			startDate: fmtDate(now),
			endDate: fmtDate(addDays(now, 90)),
			includeTransits: true,
			loading: false,
			result: null,
			requestKey: '',
		};
		this.load = this.load.bind(this);
		this.change = this.change.bind(this);
	}

	componentDidMount(){
		this.load();
	}

	componentDidUpdate(prevProps){
		const key = chartRequestKey(this.props.value, `ephemeris|${this.state.startDate}|${this.state.endDate}|${this.state.includeTransits ? 1 : 0}`);
		if(key && key !== this.state.requestKey && !this.state.loading){
			this.load();
		}
	}

	ensureLoaded(){
		const key = chartRequestKey(this.props.value, `ephemeris|${this.state.startDate}|${this.state.endDate}|${this.state.includeTransits ? 1 : 0}`);
		if(key && key !== this.state.requestKey && !this.state.loading){
			setTimeout(this.load, 0);
		}
	}

	change(key, value){
		this.setState({[key]: value});
	}

	async load(){
		if(!this.props.value){
			return;
		}
		const key = chartRequestKey(this.props.value, `ephemeris|${this.state.startDate}|${this.state.endDate}|${this.state.includeTransits ? 1 : 0}`);
		this.setState({loading: true});
		try{
			const data = await request(`${Constants.ServerRoot}/astroextra/ephemeris`, {
				body: JSON.stringify({
					...chartParams(this.props.value),
					startDate: this.state.startDate,
					endDate: this.state.endDate,
					includeTransits: this.state.includeTransits,
				}),
				timeoutMs: 90000,
			});
			this.setState({result: unwrapResult(data) || {}, loading: false, requestKey: key});
		}catch(e){
			this.setState({loading: false, requestKey: key});
		}
	}

	renderToolbar(){
		return (
			<div style={{...cardStyle, display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center'}}>
				<label>开始 <input type="date" value={this.state.startDate} onChange={(e)=>this.change('startDate', e.target.value)} /></label>
				<label>结束 <input type="date" value={this.state.endDate} onChange={(e)=>this.change('endDate', e.target.value)} /></label>
				<Checkbox checked={this.state.includeTransits} onChange={(e)=>this.change('includeTransits', e.target.checked)}>行运触发本命</Checkbox>
				<Button size="small" onClick={this.load}>刷新星历</Button>
			</div>
		);
	}

	renderEvents(rows, columns){
		return <SmallTable rows={rows || []} columns={columns} />;
	}

	renderDaily(rows){
		const planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'];
		return (
			<SmallTable
				rows={(rows || []).slice(0, 370)}
				columns={[
					{key: 'date', title: '日期'},
					...planets.map((id)=>({
						key: id,
						title: astroSymbol(id),
						render: (_v, row)=>row.positions && row.positions[id] ? fmtDegree(row.positions[id]) : '-',
					})),
				]}
			/>
		);
	}

	render(){
		this.ensureLoaded();
		const result = this.state.result || {};
		const height = this.props.height ? this.props.height - 20 : 720;
		return (
			<Spin spinning={this.state.loading}>
				<div style={{height, overflow: 'auto', paddingRight: 8}}>
					{this.renderToolbar()}
					<Tabs defaultActiveKey="events" tabPosition="top">
						<TabPane tab="事件" key="events">
							<div style={cardStyle}>
								<div className="horosa-info-card-title">入座</div>
								{this.renderEvents(result.ingresses, [
									{key: 'datetime', title: '时间'},
									{key: 'body', title: '星体', render: (v)=>astroSymbol(v)},
									{key: 'toSign', title: '进入', render: (v)=>astroSymbol(v)},
									{key: 'sign', title: '位置', render: (_v, row)=>fmtDegree(row)},
								])}
							</div>
							<div style={cardStyle}>
								<div className="horosa-info-card-title">留与顺逆转向</div>
								{this.renderEvents(result.stations, [
									{key: 'datetime', title: '时间'},
									{key: 'body', title: '星体', render: (v)=>astroSymbol(v)},
									{key: 'direction', title: '方向'},
									{key: 'sign', title: '位置', render: (_v, row)=>fmtDegree(row)},
								])}
							</div>
							<div style={cardStyle}>
								<div className="horosa-info-card-title">朔望弦</div>
								{this.renderEvents(result.lunarPhases, [
									{key: 'datetime', title: '时间'},
									{key: 'phase', title: '月相'},
									{key: 'sign', title: '月亮位置', render: (_v, row)=>fmtDegree(row)},
								])}
							</div>
							<div style={cardStyle}>
								<div className="horosa-info-card-title">食相</div>
								{this.renderEvents(result.eclipses, [
									{key: 'datetime', title: '时间'},
									{key: 'type', title: '类型'},
									{key: 'eclipseType', title: '细分'},
									{key: 'sign', title: '位置', render: (_v, row)=>fmtDegree(row)},
								])}
							</div>
						</TabPane>
						<TabPane tab="行运触发" key="transits">
							<div style={cardStyle}>
								{this.renderEvents(result.transitAspects, [
									{key: 'datetime', title: '时间'},
									{key: 'transitBody', title: '行运', render: (v)=>astroSymbol(v)},
									{key: 'aspect', title: '相位', render: (v)=>`${fmtNum(v, 0)}°`},
									{key: 'natalPoint', title: '本命', render: (v)=>astroSymbol(v)},
									{key: 'orb', title: '误差', render: (v)=>fmtNum(v, 3)},
								])}
							</div>
						</TabPane>
						<TabPane tab="每日位置" key="daily">
							<div style={cardStyle}>{this.renderDaily(result.dailyPositions)}</div>
						</TabPane>
						<TabPane tab="升落现象" key="visibility">
							<div style={cardStyle}>
								<div className="horosa-info-card-title">升落与中天</div>
								{this.renderEvents(result.riseSet, [
									{key: 'body', title: '星体', render: (v)=>astroSymbol(v)},
									{key: 'rise', title: '升起', render: (v)=>v && v.datetime ? v.datetime : '-'},
									{key: 'set', title: '落下', render: (v)=>v && v.datetime ? v.datetime : '-'},
									{key: 'upperTransit', title: '上中天', render: (v)=>v && v.datetime ? v.datetime : '-'},
									{key: 'lowerTransit', title: '下中天', render: (v)=>v && v.datetime ? v.datetime : '-'},
								])}
							</div>
							<div style={cardStyle}>
								<div className="horosa-info-card-title">行星现象</div>
								{this.renderEvents(result.phenomena, [
									{key: 'body', title: '星体', render: (v)=>astroSymbol(v)},
									{key: 'phaseAngle', title: '相位角', render: (v)=>fmtNum(v)},
									{key: 'phase', title: '照明', render: (v)=>fmtNum(v)},
									{key: 'elongation', title: '距角', render: (v)=>fmtNum(v)},
									{key: 'magnitude', title: '星等', render: (v)=>fmtNum(v)},
								])}
							</div>
							<div style={cardStyle}>
								<div className="horosa-info-card-title">晨昏偕日</div>
								{this.renderEvents(result.heliacal, [
									{key: 'body', title: '星体', render: (v)=>astroSymbol(v)},
									{key: 'rising', title: '偕日升', render: (v)=>v && v.datetime ? v.datetime : '-'},
									{key: 'setting', title: '偕日落', render: (v)=>v && v.datetime ? v.datetime : '-'},
								])}
							</div>
						</TabPane>
					</Tabs>
				</div>
			</Spin>
		);
	}
}

export default AstroEphemeris;
