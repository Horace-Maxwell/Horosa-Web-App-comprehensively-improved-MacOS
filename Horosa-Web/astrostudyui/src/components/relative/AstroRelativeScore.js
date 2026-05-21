import { Component } from 'react';
import { Spin } from 'antd';
import { XQButton as Button } from '../xq-ui';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { unwrapResult, astroSymbol, fmtNum, paramsRequestKey, cardStyle, SmallTable } from '../astro/AstroExtraCommon';

class AstroRelativeScore extends Component{
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
		const key = paramsRequestKey(this.props.params);
		if(key && key !== this.state.requestKey && !this.state.loading){
			this.load();
		}
	}

	ensureLoaded(){
		const key = paramsRequestKey(this.props.params);
		if(key && key !== this.state.requestKey && !this.state.loading){
			setTimeout(this.load, 0);
		}
	}

	async load(){
		if(!this.props.params){
			return;
		}
		const key = paramsRequestKey(this.props.params);
		this.setState({loading: true});
		try{
			const data = await request(`${Constants.ServerRoot}/astroextra/relative`, {
				body: JSON.stringify(this.props.params),
				timeoutMs: 45000,
			});
			this.setState({result: unwrapResult(data) || {}, loading: false, requestKey: key});
		}catch(e){
			this.setState({loading: false, requestKey: key});
		}
	}

	renderAspects(title, rows){
		return (
			<div style={cardStyle}>
				<div className="horosa-info-card-title">{title}</div>
				<SmallTable
					rows={rows || []}
					columns={[
						{key: 'a', title: 'A', render: (v)=>astroSymbol(v)},
						{key: 'aspect', title: '相位', render: (v)=>`${fmtNum(v, 0)}°`},
						{key: 'b', title: 'B', render: (v)=>astroSymbol(v)},
						{key: 'orb', title: '误差', render: (v)=>fmtNum(v, 3)},
						{key: 'impact', title: '权重', render: (v)=>fmtNum(v, 2)},
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
				<div style={{height: this.props.height || 640, overflow: 'auto', paddingRight: 8}}>
					<div style={cardStyle}>
						<div className="horosa-info-card-title">关系量化</div>
						<div style={{fontSize: 40, lineHeight: '48px', fontWeight: 700}}>{result.score !== undefined ? result.score : '-'}</div>
						<Button size="small" onClick={this.load}>重新计算</Button>
					</div>
					{this.renderAspects('顺畅连接', result.highlights)}
					{this.renderAspects('张力连接', result.challenges)}
					{this.renderAspects('全部权重相位', result.aspects)}
				</div>
			</Spin>
		);
	}
}

export default AstroRelativeScore;
