import { Component } from 'react';
import { Row, Col, Divider } from 'antd';
import moment from 'moment';
import AstroDoubleChart from './AstroDoubleChart';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { saveModuleAISnapshot, } from '../../utils/moduleAiSnapshot';
import { SmallTable, symbolWithMeaning } from './AstroExtraCommon';
import styles from '../../css/styles.less';
import DateTime from '../comp/DateTime';
import PlusMinusTime from './PlusMinusTime';
import { XQSelect as Select } from '../xq-ui';

const Option = Select.Option;
const RATE = { persian: 1.0, prophected: 30.0, naibod: 0.9856473 };
const RATE_LABEL = { persian: '波斯 1°/年', prophected: 'Prophected 30°/年', naibod: 'Naibod 59′08″/年' };
const MOVERS = [AstroConst.SUN, AstroConst.MOON, AstroConst.MERCURY, AstroConst.VENUS, AstroConst.MARS, AstroConst.JUPITER, AstroConst.SATURN];
const ASPECTS = [0, 60, 90, 120, 180];

function norm360(v){ let n = Number(v) % 360; if(n < 0){ n += 360; } return n; }

function lonOf(obj){
	if(!obj){ return null; }
	if(obj.lon !== undefined && obj.lon !== null){ return Number(obj.lon); }
	const i = AstroConst.LIST_SIGNS.indexOf(obj.sign);
	if(i >= 0 && obj.signlon !== undefined && obj.signlon !== null){ return i * 30 + Number(obj.signlon); }
	return null;
}

function natalParams(chartObj){
	const q = chartObj ? (chartObj.params || {}) : {};
	const params = { ...q };
	if(q.birth){ const parts = q.birth.split(' '); params.date = parts[0]; params.time = parts[1]; }
	return {
		date: params.date, time: params.time, ad: params.ad ? params.ad : 1,
		zone: params.zone, dirZone: params.zone, lon: params.lon, lat: params.lat,
		gpsLat: params.gpsLat, gpsLon: params.gpsLon, hsys: params.hsys,
		zodiacal: params.zodiacal, tradition: params.tradition,
	};
}

// 应期 hit-list（纯前端算术）：direct: directed_lon=natalLon+age*rate；converse: -age*rate（反向）。
export function buildPersianHits(chartObj, rateKey, maxAge, direction){
	const chart = (chartObj && chartObj.chart) ? chartObj.chart : {};
	const objects = Array.isArray(chart.objects) ? chart.objects : [];
	const rate = RATE[rateKey] || 1.0;
	const cap = maxAge || 90;
	const converse = direction === 'converse';
	const byId = {};
	objects.forEach((o) => { const l = lonOf(o); if(l !== null){ byId[o.id] = l; } });
	const targets = [];
	Object.keys(byId).forEach((id) => targets.push({ id, lon: byId[id] }));
	(Array.isArray(chart.houses) ? chart.houses : []).forEach((h, i) => {
		const l = lonOf(h); if(l !== null){ targets.push({ id: `${i + 1}宫头`, lon: l }); }
	});
	const birth = (chartObj && chartObj.params && chartObj.params.birth)
		? moment(`${chartObj.params.birth}`.replace(/\//g, '-'), ['YYYY-MM-DD HH:mm:ss', 'YYYY-MM-DD HH:mm', 'YYYY-MM-DD'])
		: null;
	const hits = [];
	MOVERS.forEach((p) => {
		const pl = byId[p];
		if(pl === undefined){ return; }
		targets.forEach((t) => {
			if(t.id === p){ return; }
			ASPECTS.forEach((a) => {
				[1, -1].forEach((s) => {
					if((a === 0 || a === 180) && s === -1){ return; }
					const target = norm360(t.lon + s * a);
					const arc = converse ? norm360(pl - target) : norm360(target - pl);
					const age = arc / rate;
					if(age > 0 && age <= cap){
						const date = (birth && birth.isValid()) ? birth.clone().add(age * 365.2421904, 'days').format('YYYY-MM-DD') : '';
						hits.push({ age: Math.round(age * 100) / 100, promittor: p, aspect: a, significator: t.id, date });
					}
				});
			});
		});
	});
	hits.sort((x, y) => x.age - y.age);
	return hits;
}

export function buildPersianDirectedSnapshotText(chartObj){
	if(!chartObj){ return ''; }
	const hits = buildPersianHits(chartObj, 'persian', 90, 'direct');
	if(!hits.length){ return ''; }
	const sym = (id) => (AstroText.AstroTxtMsg[id] || `${id}`);
	const asp = (deg) => (AstroText.AstroTxtMsg['Asp' + deg] || `${deg}°`);
	const lines = [];
	lines.push('[波斯向运（Persian Directed）]');
	lines.push('黄经象征向运(1°/年)：所有行星/点每年 +1°,本命宫头不动；下表为向运星触及本命的应期。');
	lines.push('');
	lines.push('| 年龄 | 日期 | 向运星 | 相位 | 本命对象 |');
	lines.push('| --- | --- | --- | --- | --- |');
	hits.slice(0, 120).forEach((h) => {
		lines.push(`| ${h.age} | ${h.date || '-'} | ${sym(h.promittor)} | ${asp(h.aspect)} | ${sym(h.significator)} |`);
	});
	return lines.join('\n');
}

class AstroPersianDirected extends Component{
	constructor(props){
		super(props);
		const np = natalParams(props.value);
		const dt = new DateTime();
		dt.addDate(1);
		this.state = { params: { ...np, datetime: dt, asporb: 1, nodeRetrograde: false, rateKey: 'persian', direction: 'direct' }, dirChart: null };
		this.requestDirection = this.requestDirection.bind(this);
		this.requestData = this.requestData.bind(this);
		this.changeRate = this.changeRate.bind(this);
		this.changeDirection = this.changeDirection.bind(this);
		this.handleTimeChanged = this.handleTimeChanged.bind(this);
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);
	}

	componentDidMount(){
		this.requestData();
		this.saveSnapshot();
		if(typeof window !== 'undefined'){
			window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}

	componentDidUpdate(prevProps){
		if(prevProps.value !== this.props.value){
			this.requestData();
			this.saveSnapshot();
		}
	}

	componentWillUnmount(){
		if(typeof window !== 'undefined'){
			window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}

	saveSnapshot(){
		const txt = buildPersianDirectedSnapshotText(this.props.value);
		saveModuleAISnapshot('persiandirected', txt, { tab: 'persiandirected' });
		return txt;
	}

	handleSnapshotRefreshRequest(evt){
		if(!evt || !evt.detail || evt.detail.module !== 'persiandirected'){ return; }
		const txt = this.saveSnapshot();
		if(txt){ evt.detail.snapshotText = txt; }
	}

	requestData(){
		// 每次请求都从当前 props.value 重算本命参数(date/time/lat/lon/zone…)。
		// 否则组件构造时绑定的旧盘会把内圈本命冻结成错误日期：换盘后 componentDidUpdate
		// 只重新请求、不重算 natalParams，内圈本命会被后端按旧 date 起盘(实测对不上选择的盘)。
		const np = natalParams(this.props.value);
		const params = { ...this.state.params, ...np };
		params.datetime = params.datetime.format ? params.datetime.format('YYYY-MM-DD HH:mm') : params.datetime;
		if(this.props.value){ this.requestDirection(params); }
	}

	async requestDirection(params){
		try{
			const data = await request(`${Constants.ServerRoot}/predict/persianchart`, { body: JSON.stringify(params) });
			const result = data[Constants.ResultKey];
			const tm = new DateTime();
			const dt = tm.parse(params.datetime, 'YYYY-MM-DD HH:mm:ss');
			if(params.dirZone){ dt.setZone(params.dirZone); }
			this.setState({ dirChart: result, params: { ...params, datetime: dt } });
		}catch(e){ /* ignore */ }
	}

	changeRate(v){
		const params = { ...this.state.params, rateKey: v };
		this.setState({ params }, () => {
			const p = { ...params, datetime: params.datetime.format ? params.datetime.format('YYYY-MM-DD HH:mm') : params.datetime };
			if(this.props.value){ this.requestDirection(p); }
		});
	}

	changeDirection(v){
		const params = { ...this.state.params, direction: v };
		this.setState({ params }, () => {
			const p = { ...params, datetime: params.datetime.format ? params.datetime.format('YYYY-MM-DD HH:mm') : params.datetime };
			if(this.props.value){ this.requestDirection(p); }
		});
	}

	handleTimeChanged(val){
		if(!val || !val.time){ return; }
		const next = val.time instanceof DateTime ? val.time : val.time.time;
		if(!next){ return; }
		const params = { ...this.state.params, datetime: next.clone ? next.clone() : next };
		this.setState({ params }, () => {
			const p = { ...params, datetime: params.datetime.format ? params.datetime.format('YYYY-MM-DD HH:mm') : params.datetime };
			if(this.props.value){ this.requestDirection(p); }
		});
	}

	render(){
		const chartObj = { natualChart: this.props.value, dirChart: this.state.dirChart };
		const rateKey = this.state.params.rateKey;
		const direction = this.state.params.direction || 'direct';
		const hits = buildPersianHits(this.props.value, rateKey, 90, direction);
		let birthDt = null;
		try{
			const b = this.props.value && this.props.value.params ? this.props.value.params.birth : '';
			if(b){ const d = new DateTime(); d.parse(`${b}`, 'YYYY-MM-DD HH:mm:ss'); birthDt = d; }
		}catch(e){ birthDt = null; }
		const curDt = this.state.params.datetime;
		const sym = (id) => (AstroText.AstroTxtMsg[id] || `${id}`);
		const asp = (deg) => (AstroText.AstroTxtMsg['Asp' + deg] || `${deg}°`);
		const height = this.props.height ? this.props.height : 760;
		const style = { height: (height - 20) + 'px', overflowY: 'auto', overflowX: 'hidden' };
		return (
			<div>
				<Row gutter={6}>
					<Col span={17}>
						<AstroDoubleChart value={chartObj} height={height}
							planetDisplay={this.props.planetDisplay} lotsDisplay={this.props.lotsDisplay}
							chartDisplay={this.props.chartDisplay} showAstroMeaning={this.props.showAstroMeaning} />
					</Col>
					<Col span={7}>
						<div className={styles.scrollbar} style={style}>
							<Row gutter={8} style={{ marginBottom: 8 }}>
								<Col span={12}>
									<div style={{ marginBottom: 4 }}>向运速率</div>
									<Select value={rateKey} onChange={this.changeRate} style={{ width: '100%' }}>
										{Object.keys(RATE).map((k) => <Option value={k} key={k}>{RATE_LABEL[k]}</Option>)}
									</Select>
								</Col>
								<Col span={12}>
									<div style={{ marginBottom: 4 }}>向运方向</div>
									<Select value={direction} onChange={this.changeDirection} style={{ width: '100%' }}>
										<Option value="direct">Direct（逆时针）</Option>
										<Option value="converse">Converse（顺时针）</Option>
									</Select>
								</Col>
							</Row>
							<div style={{ marginBottom: 8 }}>
								<div style={{ marginBottom: 4 }}>推运时间（驱动左盘）</div>
								<PlusMinusTime
									value={curDt}
									startTime={birthDt || undefined}
									needZone={false}
									showAdjust={true}
									onAfterChanged={this.handleTimeChanged}
								/>
							</div>
							<div style={{ fontSize: 12, color: 'var(--horosa-muted, #666)', marginBottom: 6 }}>左侧双盘：内圈本命、外圈向运（宫头固定本命）。调上方时间即推运左盘。</div>
							<Divider orientation="left">应期（向运 → 本命）</Divider>
							<SmallTable
								rowKey={(r, i) => i}
								rows={hits.slice(0, 200)}
								columns={[
									{ key: 'age', title: '年龄', render: (v) => v },
									{ key: 'date', title: '日期', render: (v) => v || '-' },
									{ key: 'promittor', title: '向运', render: (v) => symbolWithMeaning(v, this.props.showAstroMeaning) },
									{ key: 'aspect', title: '相位', render: (v) => asp(v) },
									{ key: 'significator', title: '本命', render: (v) => (AstroConst.LIST_SIGNS.indexOf(v) >= 0 ? v : symbolWithMeaning(v, this.props.showAstroMeaning)) },
								]}
							/>
						</div>
					</Col>
				</Row>
			</div>
		);
	}
}

export default AstroPersianDirected;
