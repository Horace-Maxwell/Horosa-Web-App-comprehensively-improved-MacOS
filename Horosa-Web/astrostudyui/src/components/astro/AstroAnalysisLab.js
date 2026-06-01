import { Component } from 'react';
import { Spin } from 'antd';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { unwrapResult, astroSymbol, astroSymbolList, fmtDegree, fmtNum, chartParams, chartRequestKey, cardStyle, gridStyle, SmallTable } from './AstroExtraCommon';

class AstroAnalysisLab extends Component{
	constructor(props){
		super(props);
		this.state = {
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
		const key = chartRequestKey(this.props.value, 'analysis');
		if(key && key !== this.state.requestKey && !this.state.loading){
			this.load();
		}
	}

	ensureLoaded(){
		const key = chartRequestKey(this.props.value, 'analysis');
		if(key && key !== this.state.requestKey && !this.state.loading){
			setTimeout(this.load, 0);
		}
	}

	async load(){
		if(!this.props.value){
			return;
		}
		const key = chartRequestKey(this.props.value, 'analysis');
		this.setState({loading: true});
		try{
			const data = await request(`${Constants.ServerRoot}/astroextra/analysis`, {
				body: JSON.stringify({
					...chartParams(this.props.value),
					fixedStarOrb: 1,
				}),
				silent: true,
				timeoutMs: 30000,
			});
			this.setState({result: unwrapResult(data) || {}, loading: false, requestKey: key});
		}catch(e){
			this.setState({loading: false, requestKey: key});
		}
	}

	renderPatterns(patterns){
		return (
			<div style={cardStyle}>
				<div className="horosa-info-card-title">相位格局</div>
				{patterns && patterns.length ? (
					<div style={gridStyle}>
						{patterns.map((item, idx)=>(
							<div key={`${item.type}-${idx}`} style={{padding: 8, border: '1px solid rgba(148,163,184,.22)', borderRadius: 6}}>
								<strong>{item.label}</strong>
								<div>{astroSymbolList(item.points)}</div>
								{item.apex ? <div>顶点：{astroSymbol(item.apex)}</div> : null}
								{item.sign ? <div>星座：{astroSymbol(item.sign)}</div> : null}
								{item.span !== undefined ? <div>跨度：{fmtNum(item.span)}°</div> : null}
							</div>
						))}
					</div>
				) : <div>未检出主要格局。</div>}
			</div>
		);
	}

	renderDistribution(dist){
		if(!dist){
			return null;
		}
		const rows = [];
		Object.keys(dist.elements || {}).forEach((key)=>rows.push({group: '元素', key, value: dist.elements[key]}));
		Object.keys(dist.modes || {}).forEach((key)=>rows.push({group: '模式', key, value: dist.modes[key]}));
		Object.keys(dist.hemispheres || {}).forEach((key)=>rows.push({group: '半球', key, value: dist.hemispheres[key]}));
		return (
			<div style={cardStyle}>
				<div className="horosa-info-card-title">分布权重</div>
				<SmallTable
					rows={rows}
					columns={[
						{key: 'group', title: '分类'},
						{key: 'key', title: '项目'},
						{key: 'value', title: '数量'},
					]}
				/>
			</div>
		);
	}

	renderAlmutem(almutem){
		if(!almutem){
			return null;
		}
		const totals = Object.keys(almutem.totals || {}).map((key)=>({
			planet: key,
			score: almutem.totals[key],
		})).sort((a, b)=>b.score - a.score);
		return (
			<div style={cardStyle}>
				<div className="horosa-info-card-title">Almuten 与古典得分</div>
				<div style={{marginBottom: 8}}>总主：{astroSymbol(almutem.winner)}</div>
				<SmallTable
					rows={totals}
					columns={[
						{key: 'planet', title: '星体', render: (val)=>astroSymbol(val)},
						{key: 'score', title: '分数'},
					]}
				/>
			</div>
		);
	}

	renderTemperament(temp){
		if(!temp){
			return null;
		}
		const rows = [];
		Object.keys(temp.temperaments || {}).forEach((key)=>rows.push({group: '气质', key, value: temp.temperaments[key]}));
		Object.keys(temp.qualities || {}).forEach((key)=>rows.push({group: '性质', key, value: temp.qualities[key]}));
		return (
			<div style={cardStyle}>
				<div className="horosa-info-card-title">气质评估</div>
				<SmallTable
					rows={rows}
					columns={[
						{key: 'group', title: '分类'},
						{key: 'key', title: '项目'},
						{key: 'value', title: '分数'},
					]}
				/>
			</div>
		);
	}

	renderLots(lots){
		return (
			<div style={cardStyle}>
				<div className="horosa-info-card-title">点库与扩展希腊点</div>
				<SmallTable
					rows={(lots || []).slice(0, 80)}
					columns={[
						{key: 'label', title: '点'},
						{key: 'sign', title: '位置', render: (_v, row)=>fmtDegree(row)},
						{key: 'formula', title: '来源'},
					]}
				/>
			</div>
		);
	}

	renderFixedStars(hits){
		return (
			<div style={cardStyle}>
				<div className="horosa-info-card-title">恒星触发</div>
				<SmallTable
					rows={(hits || []).slice(0, 80)}
					columns={[
						{key: 'star', title: '恒星'},
						{key: 'point', title: '触发点', render: (val)=>astroSymbol(val)},
						{key: 'sign', title: '位置', render: (_v, row)=>fmtDegree(row)},
						{key: 'orb', title: '容许度', render: (val)=>`${fmtNum(val)}°`},
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
				<div style={{height: this.props.height || 560, overflow: 'auto', paddingRight: 8}}>
					{this.renderPatterns(result.patterns)}
					{this.renderDistribution(result.distribution)}
					{this.renderAlmutem(result.almutem)}
					{this.renderTemperament(result.temperament)}
					{this.renderLots(result.extraLots)}
					{this.renderFixedStars(result.fixedStarHits)}
				</div>
			</Spin>
		);
	}
}

export default AstroAnalysisLab;
