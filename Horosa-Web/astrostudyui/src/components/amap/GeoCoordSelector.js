import { Component } from 'react';
import MapV2 from './MapV2';
import PropTypes from 'prop-types';
import { XQInput as Input, XQButton as Button } from '../xq-ui';
import { uuid, randomStr, gcj02ToGps, gpsToGcj02 } from '../../utils/helper';
import { safeLoadAMapUI } from './amapUIHelper';
import { dstAwareZoneAt } from '../../utils/timezone';
import CITIES from '../../data/cities.json';
import styles from './GeoCoordSelector.less';

// 成熟 atlas 地点选择：左栏「城市快搜 + 手输经纬」+ 右栏「高德地图选点/地名搜索」，
// 顶部实时显示当前 GPS 经纬度 + 依经纬度+日期自动推算的时区（含夏令时）。城市库离线可用，地图需联网。
class GeoCoordSelector extends Component{

	constructor(props) {
		super(props);
		this.state = {
			map: null,
			mapid: 'div' + randomStr(8),
			autoCompleteInputId: 'auinput_' + uuid(16, 16),
			autoSearch: null,
			marker: null,
			cityKeyword: '',
			manualLat: props.gpsLat !== undefined && props.gpsLat !== null ? `${props.gpsLat}` : '',
			manualLng: props.gpsLng !== undefined && props.gpsLng !== null ? `${props.gpsLng}` : '',
		};
		this.handleMapCreated = this.handleMapCreated.bind(this);
		this.handleSearchSelect = this.handleSearchSelect.bind(this);
		this.handleMapClick = this.handleMapClick.bind(this);
		this.changePos = this.changePos.bind(this);
		this.applyGps = this.applyGps.bind(this);
		this.onManualApply = this.onManualApply.bind(this);
	}

	// info.lat/lng 为高德 GCJ-02 坐标 → 转 GPS 回填。
	changePos(info){
		if(this.props.onChange){
			const geo = gcj02ToGps(info.lat, info.lng);
			info.gpsLat = geo.lat;
			info.gpsLng = geo.lon;
			this.props.onChange(info);
		}
	}

	// 直接按 GPS（城市库 / 手输）选点：GPS → GCJ 供地图显示，回填 GPS。
	applyGps(gpsLat, gpsLng){
		const lat = Number(gpsLat);
		const lng = Number(gpsLng);
		if(!Number.isFinite(lat) || !Number.isFinite(lng)){
			return;
		}
		const gcj = gpsToGcj02(lat, lng);
		this.setState({ manualLat: `${lat}`, manualLng: `${lng}` });
		if(this.props.onChange){
			this.props.onChange({ lat: gcj.lat, lng: gcj.lon, gpsLat: lat, gpsLng: lng });
		}
	}

	onManualApply(){
		this.applyGps(this.state.manualLat, this.state.manualLng);
	}

	handleMapCreated(map){
		if(this.state.autoSearch){
			return;
		}
		map.on('click', this.handleMapClick);
		const marker = new window.AMap.Marker({ position: new window.AMap.LngLat(116.39, 39.9) });
		map.add(marker);
		safeLoadAMapUI(['control/BasicControl'], (BasicControl)=>{
			map.addControl(new BasicControl.Zoom({ position: 'lt', showZoomNum: false }));
		});
		map.plugin(['AMap.AutoComplete'], ()=>{
			const auto = new window.AMap.AutoComplete({ input: this.state.autoCompleteInputId });
			auto.on('select', this.handleSearchSelect);
			this.setState({ map, autoSearch: auto });
		});
		this.setState({ marker });
	}

	handleSearchSelect(e){
		if(e.poi && e.poi.location){
			this.state.map.setZoom(13);
			this.state.map.setCenter(e.poi.location);
			this.state.marker.setPosition(e.poi.location);
			this.changePos({ lat: e.poi.location.lat, lng: e.poi.location.lng });
		}
	}

	handleMapClick(e){
		this.changePos({ lat: e.lnglat.lat, lng: e.lnglat.lng });
	}

	filteredCities(){
		const kw = `${this.state.cityKeyword || ''}`.trim().toLowerCase();
		if(!kw){
			return CITIES.slice(0, 60);
		}
		return CITIES.filter((c)=>{
			return `${c.name}`.toLowerCase().indexOf(kw) >= 0
				|| `${c.en || ''}`.toLowerCase().indexOf(kw) >= 0
				|| `${c.region || ''}`.toLowerCase().indexOf(kw) >= 0;
		}).slice(0, 60);
	}

	resolveDateStr(){
		const d = this.props.date;
		if(d && typeof d.format === 'function'){
			try{ return d.format('YYYY-MM-DD'); }catch(e){ /* noop */ }
		}
		if(typeof d === 'string' && d){
			return d.slice(0, 10);
		}
		// 兜底用今天：让弹窗时区预览始终可算（真实换算由表单 changeGeo→applyDstToFields 按出生日期处理）。
		const now = new Date();
		const p = (n)=>`${n}`.padStart(2, '0');
		return `${now.getFullYear()}-${p(now.getMonth() + 1)}-${p(now.getDate())}`;
	}

	renderTzPreview(){
		const { gpsLat, gpsLng } = this.props;
		if(gpsLat === undefined || gpsLat === null || gpsLng === undefined || gpsLng === null){
			return <span className={styles.tzNone}>选择地点后自动推算时区</span>;
		}
		let info = null;
		try{ info = dstAwareZoneAt(Number(gpsLat), Number(gpsLng), this.resolveDateStr()); }catch(e){ info = null; }
		if(!info || !info.zone){
			return <span className={styles.tzNone}>时区：未知</span>;
		}
		return (
			<span className={styles.tzInfo}>
				<span className={styles.tzZone}>{info.zone}</span>
				<span className={styles.tzOffset}>UTC{info.offset}</span>
				{info.dst ? <span className={styles.tzDst}>夏令时</span> : null}
			</span>
		);
	}

	render(){
		const hasPos = this.props.gpsLat !== undefined && this.props.gpsLat !== null
			&& this.props.gpsLng !== undefined && this.props.gpsLng !== null;
		if(hasPos && this.state.map){
			const pos = new window.AMap.LngLat(this.props.lng, this.props.lat);
			if(this.state.marker){ this.state.marker.setPosition(pos); }
			this.state.map.setCenter(pos);
		}
		const cities = this.filteredCities();

		return (
			<div className={styles.atlas}>
				<div className={styles.head}>
					<div className={styles.coord}>
						{hasPos
							? <span><b>经</b> {Number(this.props.gpsLng).toFixed(4)} · <b>纬</b> {Number(this.props.gpsLat).toFixed(4)}</span>
							: <span className={styles.coordNone}>尚未选择地点</span>}
					</div>
					<div className={styles.tz}>{this.renderTzPreview()}</div>
				</div>
				<div className={styles.body}>
					<div className={styles.side}>
						<div className={styles.sideLabel}>城市快搜</div>
						<Input
							allowClear
							value={this.state.cityKeyword}
							placeholder="搜城市 / 拼音 / 地区"
							onChange={(e)=>this.setState({ cityKeyword: e.target.value })}
						/>
						<div className={styles.cityList}>
							{cities.length === 0 ? (
								<div className={styles.cityEmpty}>无匹配城市，可用右侧地图或下方手输</div>
							) : cities.map((c)=>(
								<button
									type="button"
									key={`${c.name}-${c.lat}-${c.lng}`}
									className={styles.cityItem}
									onClick={()=>this.applyGps(c.lat, c.lng)}
								>
									<span className={styles.cityName}>{c.name}</span>
									<span className={styles.cityRegion}>{c.region || ''}</span>
								</button>
							))}
						</div>
						<div className={styles.sideLabel}>手输经纬度（GPS 十进制）</div>
						<div className={styles.manualRow}>
							<Input
								value={this.state.manualLng}
								placeholder="经度"
								onChange={(e)=>this.setState({ manualLng: e.target.value })}
								onPressEnter={this.onManualApply}
							/>
							<Input
								value={this.state.manualLat}
								placeholder="纬度"
								onChange={(e)=>this.setState({ manualLat: e.target.value })}
								onPressEnter={this.onManualApply}
							/>
							<Button type="primary" onClick={this.onManualApply}>应用</Button>
						</div>
					</div>
					<div className={styles.mapWrap}>
						<Input
							className={styles.mapSearch}
							placeholder="在地图上搜索地名"
							id={this.state.autoCompleteInputId}
						/>
						<div id={this.state.mapid} className={styles.map}>
							<MapV2
								zoom={this.props.zoom ? this.props.zoom : 11}
								plugin={['AMap.AutoComplete']}
								uiplugin={['control/BasicControl', 'overlay/SimpleMarker']}
								created={this.handleMapCreated}
							/>
						</div>
					</div>
				</div>
			</div>
		);
	}
}

GeoCoordSelector.propTypes = {
	width: PropTypes.any,
	height: PropTypes.any,
	zoom: PropTypes.number,
	lat: PropTypes.number,
	lng: PropTypes.number,
	gpsLat: PropTypes.any,
	gpsLng: PropTypes.any,
	date: PropTypes.any,
	onChange: PropTypes.func,
};

export default GeoCoordSelector;
