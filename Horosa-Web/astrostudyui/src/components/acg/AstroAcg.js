import { Component } from 'react';
import { Row, Col } from 'antd';
import AcgD3Map, { STYLES } from './AcgD3Map';
import AcgPointPanel from './AcgPointPanel';
import request from '../../utils/request';
import DateTimeInfo from '../comp/DateTimeInfo';
import * as Constants from '../../utils/constants';
import AstroLinesSelector from './AstroLinesSelector';
import { getAllLines } from './AcgHelper';
import { XQButton, XQDrawer } from '../xq-ui';

function fieldsToParams(fields) {
	return {
		ad: fields.date.value.ad,
		date: fields.date.value.format('YYYY/MM/DD'),
		time: fields.time.value.format('HH:mm:ss'),
		zone: fields.date.value.zone,
		lat: fields.lat.value,
		lon: fields.lon.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		name: fields.name.value,
		pos: fields.pos.value,
	};
}

class AstroAcg extends Component {
	constructor(props) {
		super(props);
		const lines = getAllLines();

		this.state = {
			acgData: null,
			drawerVisible: false,
			lines: lines,
			linesSet: new Set(lines),
			projection: 'equirect',
			mapStyle: 'classic',
			showGeo: true,
			showLS: false,
			paranMode: 'off',
			showLabels: true,
			pointReport: null,
			pointOpen: false,
			pointLoading: false,
			clickMarker: null,
		};

		this.unmounted = false;

		this.requestAcg = this.requestAcg.bind(this);
		this.genParams = this.genParams.bind(this);
		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.closeDrawer = this.closeDrawer.bind(this);
		this.openDrawer = this.openDrawer.bind(this);
		this.changeLines = this.changeLines.bind(this);
		this.toggleProjection = this.toggleProjection.bind(this);
		this.cycleStyle = this.cycleStyle.bind(this);
		this.cycleParan = this.cycleParan.bind(this);
		this.toggle = this.toggle.bind(this);
		this.onMapClick = this.onMapClick.bind(this);
		this.closePoint = this.closePoint.bind(this);

		if (this.props.hook) {
			this.props.hook.fun = () => {
				if (this.unmounted) return;
				this.requestAcg(this.genParams());
			};
		}
	}

	toggleProjection() {
		this.setState({ projection: this.state.projection === 'equirect' ? 'mercator' : 'equirect' });
	}

	cycleStyle() {
		const keys = Object.keys(STYLES);
		const i = keys.indexOf(this.state.mapStyle);
		this.setState({ mapStyle: keys[(i + 1) % keys.length] });
	}

	cycleParan() {
		const order = ['off', 'lum', 'all'];
		const i = order.indexOf(this.state.paranMode);
		this.setState({ paranMode: order[(i + 1) % order.length] });
	}

	toggle(key) {
		this.setState({ [key]: !this.state[key] });
	}

	changeLines(vals) {
		this.setState({ lines: vals, linesSet: new Set(vals) });
	}

	closeDrawer() { this.setState({ drawerVisible: false }); }
	openDrawer() { this.setState({ drawerVisible: true }); }
	closePoint() { this.setState({ pointOpen: false }); }

	async requestAcg(params) {
		const data = await request(`${Constants.ServerRoot}/location/acg`, { body: JSON.stringify(params) });
		if (this.unmounted) return;
		this.setState({ acgData: data[Constants.ResultKey] });
	}

	async onMapClick(lat, lon) {
		this.setState({ clickMarker: { lat, lon }, pointOpen: true, pointLoading: true });
		try {
			const params = { ...this.genParams(), clickLat: lat, clickLon: lon, orb: 2 };
			const data = await request(`${Constants.ServerRoot}/location/acgpoint`, { body: JSON.stringify(params) });
			if (this.unmounted) return;
			this.setState({ pointReport: data[Constants.ResultKey], pointLoading: false });
		} catch (e) {
			if (!this.unmounted) this.setState({ pointLoading: false });
		}
	}

	genParams() { return fieldsToParams(this.props.fields); }

	onFieldsChange(values) {
		if (this.props.onChange) {
			const flds = this.props.onChange(values);
			this.requestAcg(fieldsToParams(flds));
		}
	}

	componentDidMount() {
		this.unmounted = false;
		this.requestAcg(this.genParams());
	}

	componentWillUnmount() { this.unmounted = true; }

	render() {
		const fields = this.props.fields;
		let height = this.props.height ? this.props.height : 760;
		height = height - 50;
		const dt = fields.date ? fields.date.value : null;
		const s = this.state;
		const btn = (label, onClick, active) => (
			<XQButton size="small" type={active ? 'primary' : 'default'} style={{ marginLeft: 8 }} onClick={onClick}>{label}</XQButton>
		);

		return (
			<div className="horosa-acg-page xq-chart-renderer xq-chart-renderer-locastro">
				<Row align="middle">
					<Col span={7}>
						<DateTimeInfo value={dt} />
					</Col>
					<Col span={17} style={{ textAlign: 'right', marginBottom: 10 }}>
						<XQButton size="small" onClick={this.openDrawer}>行星线选择</XQButton>
						{btn(s.showGeo ? '参考线开' : '参考线关', () => this.toggle('showGeo'), s.showGeo)}
						{btn(s.showLS ? '本地空间开' : '本地空间', () => this.toggle('showLS'), s.showLS)}
						{btn(s.paranMode === 'all' ? 'Parans·全部' : s.paranMode === 'lum' ? 'Parans·日月' : 'Parans', this.cycleParan, s.paranMode !== 'off')}
						{btn(s.showLabels ? '标注开' : '标注关', () => this.toggle('showLabels'), s.showLabels)}
						{btn(s.projection === 'equirect' ? '等距投影' : '墨卡托', this.toggleProjection, false)}
						{btn('样式·' + ((STYLES[s.mapStyle] && STYLES[s.mapStyle].name) || ''), this.cycleStyle, false)}
					</Col>
				</Row>
				<Row>
					<Col span={24}>
						<AcgD3Map
							value={s.acgData}
							fields={fields}
							height={height}
							lines={s.linesSet}
							projection={s.projection}
							mapStyle={s.mapStyle}
							showGeo={s.showGeo}
							showLS={s.showLS}
							showParans={s.paranMode !== 'off'}
							paranAll={s.paranMode === 'all'}
							showLabels={s.showLabels}
							clickMarker={s.clickMarker}
							onMapClick={this.onMapClick}
						/>
					</Col>
				</Row>

				<XQDrawer
					title="行星线选择"
					width={500}
					placement="left"
					onClose={this.closeDrawer}
					maskClosable={true}
					open={s.drawerVisible}
					style={{ height: 'calc(100% - 0px)', overflow: 'auto', paddingBottom: 53, backgroundColor: 'transparent' }}
				>
					<AstroLinesSelector value={s.lines} onChange={this.changeLines} />
				</XQDrawer>

				<AcgPointPanel
					open={s.pointOpen}
					loading={s.pointLoading}
					report={s.pointReport}
					onClose={this.closePoint}
				/>
			</div>
		);
	}
}

export default AstroAcg;
