import { Component } from 'react';
import { Row, Col } from 'antd';
import LatInput from '../astro/LatInput';
import LonInput from '../astro/LonInput';
import DateTimeSelector from '../comp/DateTimeSelector';
import EditableTags from '../comp/EditableTags';
import * as AstroHelper from '../astro/AstroHelper';
import GeoCoordModal from '../amap/GeoCoordModal';
import { applyDstToFields } from '../../utils/timezone';
import DstZoneIndicator from '../comp/DstZoneIndicator';
import { XQButton, XQInput, XQSelect } from '../xq-ui';

const Option = XQSelect.Option;

export default class ChartData extends Component{
	constructor(props) {
		super(props);
		this.state = {
			orgFields: this.props.fields,
			fields: {
				...this.props.fields
			},
		}

		this.submitted = false;
		this.zoneManual = false;

		this.setValue = this.setValue.bind(this);
		this.changeBirth = this.changeBirth.bind(this);
		this.changeIsPub = this.changeIsPub.bind(this);
		this.changeGroup = this.changeGroup.bind(this);
		this.changeName = this.changeName.bind(this);
		this.changeGender = this.changeGender.bind(this);
		this.changePos = this.changePos.bind(this);
		this.changeLat = this.changeLat.bind(this);
		this.changeLon = this.changeLon.bind(this);
		this.changeGeo = this.changeGeo.bind(this);
		this.applySuggestedZone = this.applySuggestedZone.bind(this);
		this.clickOk = this.clickOk.bind(this);
		this.clickReturn = this.clickReturn.bind(this);

	}


	setValue(key, val){
		let flds = this.state.fields;
		flds[key].value = val;
		this.setState({
			fields: flds,
		});
	}

	changeBirth(val){
		let tm = val.value;
		let flds = this.state.fields;
		const prevZone = flds.zone.value;
		const prevDate = (flds.birth.value && flds.birth.value.format) ? flds.birth.value.format('YYYY-MM-DD') : null;
		const newZone = tm.zone;
		const newDate = tm.format ? tm.format('YYYY-MM-DD') : null;
		flds.birth.value = tm.clone();
		flds.zone.value = newZone;
		if(newZone !== prevZone){
			// 用户手动改了时区 → 标记手动,后续不再自动覆盖
			this.zoneManual = true;
		}else if(newDate !== prevDate && !this.zoneManual){
			// 仅日期变化(可能跨夏令时边界)→ 按新日期重算时区偏移
			applyDstToFields(flds);
		}
		this.setState({
			fields: flds,
		});
	}

	changeIsPub(val){
		this.setValue('isPub', val);
	}

	changeGroup(val){
		this.setValue('group', val);
	}

	changeName(e){
		let val = e.target.value;
		this.setValue('name', val);
	}

	changeGender(val){
		this.setValue('gender', val);
	}

	changePos(e){
		let val = e.target.value;
		this.setValue('pos', val);
	}

	changeLat(val){
		let flds = this.state.fields;
		let lat = val;
		let lon = flds.lon.value;
		let latdeg = AstroHelper.convertLatStrToDegree(lat);
		let londeg = AstroHelper.convertLonStrToDegree(lon);
		flds.lat.value = lat;
		flds.gpsLat.value = latdeg;
		flds.gpsLon.value = londeg;
		if(!this.zoneManual){
			applyDstToFields(flds);
		}
		this.setState({
			fields: flds,
		});
	}

	changeLon(val){
		let flds = this.state.fields;
		let lat = flds.lat.value;
		let lon = val;
		let latdeg = AstroHelper.convertLatStrToDegree(lat);
		let londeg = AstroHelper.convertLonStrToDegree(lon);
		flds.lon.value = lon;
		flds.gpsLat.value = latdeg;
		flds.gpsLon.value = londeg;
		if(!this.zoneManual){
			applyDstToFields(flds);
		}
		this.setState({
			fields: flds,
		});
	}

	changeGeo(geo){
        let gps = {
            lat: geo.gpsLat,
            lon: geo.gpsLng,
        };
        let latdeg = AstroHelper.splitDegree(gps.lat);
        let londeg = AstroHelper.splitDegree(gps.lon);
        let latdir = 'n';
        let londir = 'e';
        if(londeg[0] < 0){
            londir = 'w';
            londeg[0] = -londeg[0];
            londeg[1] = -londeg[1];
        }
        if(latdeg[0] < 0){
            latdir = 's';
            latdeg[0] = -latdeg[0];
            latdeg[1] = -latdeg[1];
        }
        let lat = latdeg[0] + latdir + (latdeg[1] < 10 ? '0' + latdeg[1] : latdeg[1]);
        let lon = londeg[0] + londir + (londeg[1] < 10 ? '0' + londeg[1] : londeg[1]);

		let flds = this.state.fields;
		flds.lat.value = lat;
		flds.lon.value = lon;
		flds.gpsLat.value = gps.lat;
		flds.gpsLon.value = gps.lon;
		this.zoneManual = false;        // 地图选点 = 明确换地点,恢复自动时区校正
		applyDstToFields(flds);

		this.setState({
			fields: flds,
		});
	}

	// 「改用建议」按钮:恢复自动模式并按地点+日期重算回填(共享 applyDstToFields)。
	applySuggestedZone(){
		let flds = this.state.fields;
		this.zoneManual = false;
		applyDstToFields(flds);
		this.setState({
			fields: flds,
		});
	}

	clickOk(){
		if(this.props.onOk){
			this.submitted = true;
			this.props.onOk(this.state.fields);
		}
	}

	clickReturn(){
		if(this.props.onReturn){
			this.props.onReturn();
		}
	}

	render(){
		let flds = this.state.fields;
		let margintop = 20;
		let okTitle = this.props.okTitle ? this.props.okTitle : '提交';
		let returnTitle = this.props.returnTitle ? this.props.returnTitle : '返回';

		if(this.state.orgFields !== this.props.fields || this.submitted){
			this.submitted = false;
			setTimeout(()=>{
				this.setState({
					orgFields: this.props.fields,
					fields: {
						...this.props.fields,
					}
				});
			}, 500);
		}

		return (
			<div>
				<Row gutter={12}>
					<Col span={24}>出生时间：</Col>
					<Col span={24}>
						<DateTimeSelector
							showTime={true}
							showAdjust={false}
							onChange={this.changeBirth}
							value={flds.birth.value}
						/>
					</Col>
				</Row>
				<DstZoneIndicator fields={flds} marginTop={10} onApply={this.applySuggestedZone} />
				<Row gutter={12} style={{marginTop: margintop}}>
					<Col span={8}>
						<Row>
							<Col span={24}>姓名：</Col>
							<Col span={24}>
								<XQInput placeholder='姓名' value={flds.name.value} onChange={this.changeName} />
							</Col>
						</Row>
					</Col>
					<Col span={8}>
						<Row>
							<Col span={24}>性别：</Col>
							<Col span={24}>
								<XQSelect value={flds.gender.value} onChange={this.changeGender} style={{width: '100%'}}>
									<Option value={-1}>未知</Option>
									<Option value={0}>女</Option>
									<Option value={1}>男</Option>
								</XQSelect>
							</Col>
						</Row>
					</Col>
					<Col span={8}>
						<Row>
							<Col span={24}>出生地：</Col>
							<Col span={24}>
								<XQInput placeholder='出生地'
									value={flds.pos.value}
									onChange={this.changePos}
								/>
							</Col>
						</Row>
					</Col>
				</Row>
				<Row gutter={12} style={{marginTop: margintop}}>
					<Col span={8}>
						<Row>
							<Col span={24}>纬度：</Col>
							<Col span={24}>
								<LatInput
									value={flds.lat.value}
									onChange={this.changeLat}
								/>
							</Col>
						</Row>
					</Col>
					<Col span={8}>
						<Row>
							<Col span={24}>经度：</Col>
							<Col span={24}>
								<LonInput
									value={flds.lon.value}
									onChange={this.changeLon}
								/>
							</Col>
						</Row>
					</Col>
					<Col span={8}>
						<Row>
							<Col span={24}>从地图选取经纬度：</Col>
							<Col span={24}>
								<GeoCoordModal
									onOk={this.changeGeo}
									lat={flds.gpsLat.value} lng={flds.gpsLon.value}
									date={flds.birth ? flds.birth.value : undefined}
								>
									<XQButton>经纬度选择</XQButton>
								</GeoCoordModal>
							</Col>
						</Row>
					</Col>
				</Row>
				<Row gutter={12} style={{marginTop: margintop}}>
					<Col span={8}>
						<Row>
							<Col span={24}>是否公开：</Col>
							<Col span={24}>
								<XQSelect value={flds.isPub.value} onChange={this.changeIsPub}>
									<Option value={0}>否</Option>
									<Option value={1}>是</Option>
								</XQSelect>
							</Col>
						</Row>
					</Col>
					<Col span={16}>
						<Row>
							<Col span={24}>标签：</Col>
							<Col span={24}>
								<EditableTags
									newTagLabel='添加标签' needConfirm={true}
									value={flds.group.value}
									onChange={this.changeGroup}
								/>
							</Col>
						</Row>
					</Col>
				</Row>
				<Row gutter={12} style={{marginTop: margintop}}>
					<Col offset={2} span={10}>
						<XQButton type='primary' onClick={this.clickOk}>{okTitle}</XQButton>
					</Col>
					<Col span={12}>
						<XQButton onClick={this.clickReturn}>{returnTitle}</XQButton>
					</Col>
				</Row>
			</div>
		)
	}

}
