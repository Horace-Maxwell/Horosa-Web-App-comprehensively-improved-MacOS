import { Component } from 'react';
import { Spin } from 'antd';
import { XQButton as Button } from '../xq-ui';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { unwrapResult, astroSymbol, fmtDegree, fmtNum, chartParams, chartRequestKey, cardStyle, SmallTable } from '../astro/AstroExtraCommon';

class AstroHarmonicLab extends Component{
	constructor(props){
		super(props);
		this.state = {
			harmonic: 9,
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
		const key = chartRequestKey(this.props.value, `harmonic|${this.state.harmonic}`);
		if(key && key !== this.state.requestKey && !this.state.loading){
			this.load();
		}
	}

	ensureLoaded(){
		const key = chartRequestKey(this.props.value, `harmonic|${this.state.harmonic}`);
		if(key && key !== this.state.requestKey && !this.state.loading){
			setTimeout(this.load, 0);
		}
	}

	async load(){
		if(!this.props.value){
			return;
		}
		const key = chartRequestKey(this.props.value, `harmonic|${this.state.harmonic}`);
		this.setState({loading: true});
		try{
			const data = await request(`${Constants.ServerRoot}/astroextra/harmonic`, {
				body: JSON.stringify({
					...chartParams(this.props.value),
					harmonic: this.state.harmonic,
					orb: 2,
				}),
				timeoutMs: 30000,
			});
			this.setState({result: unwrapResult(data) || {}, loading: false, requestKey: key});
		}catch(e){
			this.setState({loading: false, requestKey: key});
		}
	}

	render(){
		this.ensureLoaded();
		const result = this.state.result || {};
		return (
			<Spin spinning={this.state.loading}>
				<div style={{height: this.props.height || 640, overflow: 'auto', paddingRight: 8}}>
					<div style={{...cardStyle, display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center'}}>
						<label>调波数 <input type="number" min="1" max="360" value={this.state.harmonic} onChange={(e)=>this.setState({harmonic: e.target.value})} /></label>
						<Button size="small" onClick={this.load}>计算调波盘</Button>
						<span>当前：H{result.harmonic || this.state.harmonic}</span>
					</div>
					<div style={cardStyle}>
						<div className="horosa-info-card-title">调波位置</div>
						<SmallTable
							rows={result.positions || []}
							columns={[
								{key: 'id', title: '点', render: (v)=>astroSymbol(v)},
								{key: 'natalLon', title: '本命黄经', render: (v)=>`${fmtNum(v)}°`},
								{key: 'sign', title: '调波位置', render: (_v, row)=>fmtDegree(row)},
							]}
						/>
					</div>
					<div style={cardStyle}>
						<div className="horosa-info-card-title">调波合相/同频</div>
						<SmallTable
							rows={result.conjunctions || []}
							columns={[
								{key: 'a', title: '点A', render: (v)=>astroSymbol(v)},
								{key: 'b', title: '点B', render: (v)=>astroSymbol(v)},
								{key: 'orb', title: '误差', render: (v)=>fmtNum(v, 3)},
							]}
						/>
					</div>
				</div>
			</Spin>
		);
	}
}

export default AstroHarmonicLab;
