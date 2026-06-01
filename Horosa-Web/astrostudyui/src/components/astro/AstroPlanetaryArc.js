import { Component } from 'react';
import { Row, Col, Divider } from 'antd';
import AstroDoubleChart from './AstroDoubleChart';
import AstroDirectionForm from './AstroDirectionForm';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import { convertToArray } from '../../utils/helper';
import { saveModuleAISnapshot, } from '../../utils/moduleAiSnapshot';
import styles from '../../css/styles.less';
import DateTime from '../comp/DateTime';
import { XQSelect as Select } from '../xq-ui';

const Option = Select.Option;
const ARC_SOURCES = [AstroConst.MOON, AstroConst.MERCURY, AstroConst.VENUS, AstroConst.MARS, AstroConst.JUPITER, AstroConst.SATURN, AstroConst.SUN];

function natalParams(chartObj){
	const q = chartObj ? (chartObj.params || {}) : {};
	const params = { ...q };
	if(q.birth){
		const parts = q.birth.split(' ');
		params.date = parts[0];
		params.time = parts[1];
	}
	return {
		date: params.date, time: params.time, ad: params.ad ? params.ad : 1,
		zone: params.zone, dirZone: params.zone, lon: params.lon, lat: params.lat,
		gpsLat: params.gpsLat, gpsLon: params.gpsLon, hsys: params.hsys,
		zodiacal: params.zodiacal, tradition: params.tradition,
	};
}

function todayStr(){
	const d = new Date();
	return `${d.getFullYear()}-${`${d.getMonth() + 1}`.padStart(2, '0')}-${`${d.getDate()}`.padStart(2, '0')} 12:00:00`;
}

// 把向运盘的「向运→本命」相位网格化为 markdown 段。
function formatArcSnapshot(result, title, intro){
	if(!result || !result.chart || !Array.isArray(result.chart.aspects)){ return ''; }
	const sym = (id) => (AstroText.AstroTxtMsg[id] || `${id}`);
	const asp = (deg) => (AstroText.AstroTxtMsg['Asp' + deg] || `${deg}°`);
	const lines = [];
	lines.push(`[${title}]`);
	if(intro){ lines.push(intro); }
	lines.push('');
	lines.push('| 向运星 | 相位 | 本命星 | 误差 |');
	lines.push('| --- | --- | --- | --- |');
	let n = 0;
	result.chart.aspects.forEach((row) => {
		(row.objects || []).forEach((o) => {
			if(n >= 120){ return; }
			lines.push(`| ${sym(row.directId)} | ${asp(o.aspect)} | ${sym(o.natalId)} | ${(o.delta !== undefined ? Math.round(o.delta * 1000) / 1000 : '')} |`);
			n += 1;
		});
	});
	if(n === 0){ return ''; }
	return lines.join('\n');
}

// 行星弧 AI 快照（无头）：默认月亮弧、截至今日。无数据返回 ''。
export async function buildPlanetaryArcSnapshotText(chartObj){
	if(!chartObj){ return ''; }
	try{
		const params = { ...natalParams(chartObj), datetime: todayStr(), asporb: 1, arcSource: AstroConst.MOON };
		const data = await request(`${Constants.ServerRoot}/predict/planetaryarc`, { body: JSON.stringify(params) });
		const result = data[Constants.ResultKey];
		return formatArcSnapshot(result, '行星弧（Planetary Arc）', '行星弧(默认月亮弧)：以所选天体的二次推运移动量为弧推进全盘，看向运星对本命的相位。');
	}catch(e){
		return '';
	}
}

class AstroPlanetaryArc extends Component{
	constructor(props){
		super(props);
		const np = natalParams(props.value);
		const dt = new DateTime();
		dt.addDate(1);
		this.state = {
			params: { ...np, datetime: dt, tmType: 'y', nodeRetrograde: false, asporb: 1, arcSource: AstroConst.MOON },
			dirChart: null,
		};
		this.submit = this.submit.bind(this);
		this.fieldsChanged = this.fieldsChanged.bind(this);
		this.requestDirection = this.requestDirection.bind(this);
		this.requestData = this.requestData.bind(this);
		this.changeArcSource = this.changeArcSource.bind(this);
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);
	}

	componentDidMount(){
		this.requestData();
		if(typeof window !== 'undefined'){
			window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}

	componentWillUnmount(){
		if(typeof window !== 'undefined'){
			window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}

	handleSnapshotRefreshRequest(evt){
		if(!evt || !evt.detail || evt.detail.module !== 'planetaryarc' || !this.props.value){ return; }
		buildPlanetaryArcSnapshotText(this.props.value).then((txt) => { evt.detail.snapshotText = txt || ''; }).catch(() => {});
	}

	requestData(){
		const params = { ...this.state.params };
		params.datetime = params.datetime.format('YYYY-MM-DD HH:mm');
		if(this.props.value){ this.requestDirection(params); }
	}

	async requestDirection(params){
		const data = await request(`${Constants.ServerRoot}/predict/planetaryarc`, { body: JSON.stringify(params) });
		const result = data[Constants.ResultKey];
		const tm = new DateTime();
		const dt = tm.parse(params.datetime, 'YYYY-MM-DD HH:mm:ss');
		if(params.dirZone){ dt.setZone(params.dirZone); }
		this.setState({ dirChart: result, params: { ...params, datetime: dt } }, () => {
			saveModuleAISnapshot('planetaryarc', formatArcSnapshot(result, '行星弧（Planetary Arc）', '行星弧：以所选天体的二次推运移动量为弧推进全盘。'), { module: 'planetaryarc' });
		});
	}

	changeArcSource(v){
		const params = { ...this.state.params, arcSource: v };
		this.setState({ params }, () => {
			const p = { ...params, datetime: params.datetime.format('YYYY-MM-DD HH:mm') };
			if(this.props.value){ this.requestDirection(p); }
		});
	}

	submit(values){
		const params = { ...this.state.params };
		if(values.zone){ params.dirZone = values.zone; }
		if(values.ad){ params.ad = values.ad; }
		if(values.datetime){ params.datetime = values.datetime.format('YYYY-MM-DD HH:mm:ss'); }
		if(this.props.value){ this.requestDirection(params); }
	}

	fieldsChanged(changedFields){
		const params = { ...this.state.params };
		if(changedFields.datetime && changedFields.datetime.value){
			params.datetime = changedFields.datetime.value instanceof DateTime ? changedFields.datetime.value : changedFields.datetime.value.time;
			params.ad = changedFields.datetime.value.ad;
		}
		if(changedFields.zone && changedFields.zone.value){ params.dirZone = changedFields.zone.value; }
		if(changedFields.asporb){ params.asporb = changedFields.asporb.value; }
		if(changedFields.nodeRetrograde){ params.nodeRetrograde = changedFields.nodeRetrograde.value; }
		this.setState({ params });
	}

	render(){
		const chartObj = { natualChart: this.props.value, dirChart: this.state.dirChart };
		const param = this.state.params;
		const tm = new DateTime();
		const fields = {
			startDate: { value: tm.parse(param.date, 'YYYY-MM-DD'), name: ['startDate'] },
			datetime: { value: param.datetime, name: ['datetime'] },
			lat: { value: param.lat, name: ['lat'] },
			lon: { value: param.lon, name: ['lon'] },
			tmType: { value: param.tmType, name: ['tmType'] },
			gpsLat: { value: param.gpsLat, name: ['gpsLat'] },
			gpsLon: { value: param.gpsLon, name: ['gpsLon'] },
			nodeRetrograde: { value: param.nodeRetrograde, name: ['nodeRetrograde'] },
			asporb: { value: param.asporb, name: ['asporb'] },
			ad: { value: param.ad, name: ['ad'] },
		};
		const fieldsary = convertToArray(fields);
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
							<div style={{ marginBottom: 8 }}>
								<div style={{ marginBottom: 4 }}>弧源天体（月亮弧 / 行星弧）</div>
								<Select value={param.arcSource} onChange={this.changeArcSource} style={{ width: '100%' }}>
									{ARC_SOURCES.map((id) => <Option value={id} key={id}>{AstroText.AstroTxtMsg[id] || id}</Option>)}
								</Select>
							</div>
							<AstroDirectionForm {...fields} fieldsAry={fieldsary} onFieldsChange={this.fieldsChanged} onSubmit={this.submit} />
							<Divider orientation="left">向运星 → 本命 相位</Divider>
							<div style={{ fontSize: 12, color: 'var(--horosa-muted, #666)' }}>左侧双盘：内圈本命、外圈行星弧向运。</div>
						</div>
					</Col>
				</Row>
			</div>
		);
	}
}

export default AstroPlanetaryArc;
