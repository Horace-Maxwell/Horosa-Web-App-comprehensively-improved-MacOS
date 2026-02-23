import { Component } from 'react';
import { Row, Col, Tabs, Select } from 'antd';
import AstroChartMain from '../astro/AstroChartMain';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { randomStr, } from '../../utils/helper';
import styles from '../../css/styles.less';

function fieldsToParams(fields){
	const params = {
		date: fields.date.value.format('YYYY/MM/DD'),
		time: fields.time.value.format('HH:mm:ss'),
		ad: fields.ad.value,
		zone: fields.zone.value,
		lat: fields.lat.value,
		lon: fields.lon.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		hsys: fields.hsys.value,
		zodiacal: fields.zodiacal.value,
		tradition: fields.tradition.value,
		strongRecption: fields.strongRecption.value,
		simpleAsp: fields.simpleAsp.value,
		virtualPointReceiveAsp: fields.virtualPointReceiveAsp.value,
		predictive: 0,
		name: fields.name.value,
		pos: fields.pos.value,
	};

	return params;
}

const CHART13_CACHE_MAX = 64;
const chart13Mem = new Map();
const chart13Inflight = new Map();

function clonePlain(obj){
	if(obj === undefined || obj === null){
		return obj;
	}
	try{
		return JSON.parse(JSON.stringify(obj));
	}catch(e){
		return obj;
	}
}

function pushCache(map, key, val){
	if(!key || val === undefined || val === null){
		return;
	}
	if(map.has(key)){
		map.delete(key);
	}
	map.set(key, val);
	if(map.size > CHART13_CACHE_MAX){
		const first = map.keys().next().value;
		if(first){
			map.delete(first);
		}
	}
}

function buildChart13Key(params){
	try{
		return JSON.stringify(params || {});
	}catch(e){
		return '';
	}
}

async function fetchChart13Cached(params, silent){
	const key = buildChart13Key(params);
	if(key && chart13Mem.has(key)){
		return clonePlain(chart13Mem.get(key));
	}
	if(key && chart13Inflight.has(key)){
		const inflight = await chart13Inflight.get(key);
		return clonePlain(inflight);
	}
	const req = request(`${Constants.ServerRoot}/chart13`, {
		body: JSON.stringify(params),
		silent: !!silent,
	}).then((data)=>{
		const result = data && data[Constants.ResultKey] ? data[Constants.ResultKey] : null;
		if(key && result){
			pushCache(chart13Mem, key, clonePlain(result));
		}
		return result;
	}).finally(()=>{
		if(key){
			chart13Inflight.delete(key);
		}
	});
	if(key){
		chart13Inflight.set(key, req);
	}
	const result = await req;
	return clonePlain(result);
}

class AstroChart13 extends Component{
	constructor(props) {
		super(props);
		this.state = {
			chartObj: null,
		};

		this.unmounted = false;
		this.chartReqSeq = 0;
		this.prefetchTimer = null;

		this.requestChart = this.requestChart.bind(this);
		this.genParams = this.genParams.bind(this);
		this.onFieldsChange = this.onFieldsChange.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (chartObj)=>{
				if(this.unmounted){
					return;
				}
				let params = this.genParams();
				this.requestChart(params);
			};
		}

	}

	async requestChart(params){
		if(!params){
			return;
		}
		const seq = ++this.chartReqSeq;
		const result = await fetchChart13Cached(params, true);
		if(this.unmounted || seq !== this.chartReqSeq){
			return;
		}
		if(!result){
			return;
		}

		const st = {
			chartObj: result,
		};

		this.setState(st);
	}

	genParams(){
		let fields = this.props.fields;
		let params = fieldsToParams(fields);
		return params;
	}

	onFieldsChange(values){
		if(this.props.onChange){
			let flds = this.props.onChange(values);
			if(!flds){
				return;
			}
			let params = fieldsToParams(flds);
			const unconfirmed = values && Object.prototype.hasOwnProperty.call(values, 'confirmed') && values.confirmed === false;
			if(unconfirmed){
				if(this.prefetchTimer){
					clearTimeout(this.prefetchTimer);
				}
				this.prefetchTimer = setTimeout(()=>{
					if(this.unmounted){
						return;
					}
					fetchChart13Cached(params, true).catch(()=>{
						return null;
					});
				}, 240);
				return;
			}
			if(this.prefetchTimer){
				clearTimeout(this.prefetchTimer);
				this.prefetchTimer = null;
			}
			this.requestChart(params);
		}		
	}

	componentDidMount(){
		this.unmounted = false;

		let params = this.genParams();
		this.requestChart(params);
	}

	componentWillUnmount(){
		this.unmounted = true;
		if(this.prefetchTimer){
			clearTimeout(this.prefetchTimer);
			this.prefetchTimer = null;
		}
	}

	render(){
		let chartObj = this.state.chartObj;
		let fields = this.props.fields;
		let height = this.props.height ? this.props.height : 760;

		return (
			<div>
				<AstroChartMain 
					value={chartObj} 
					onChange={this.onFieldsChange}
					hidehsys={1}
					hidezodiacal={1}
					fields={fields} 
					height={height} 
					chartDisplay={this.props.chartDisplay}
					planetDisplay={this.props.planetDisplay}
					lotsDisplay={this.props.lotsDisplay}
					showPlanetHouseInfo={this.props.showPlanetHouseInfo}
				/>
			</div>
		);
	}
}

export default AstroChart13;
