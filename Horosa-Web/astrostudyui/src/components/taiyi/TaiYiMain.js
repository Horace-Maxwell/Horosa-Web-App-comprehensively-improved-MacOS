import { Component } from 'react';
import { Spin } from 'antd';
import { XQButton as Button, XQCard as Card, XQSelect as Select, XQTabs as Tabs } from '../xq-ui';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import { fetchPreciseNongli } from '../../utils/preciseCalcBridge';
import { setNongliLocalCache } from '../../utils/localCalcCache';
import GeoCoordModal from '../amap/GeoCoordModal';
import PlusMinusTime from '../astro/PlusMinusTime';
import DateTime from '../comp/DateTime';
import SpaceTimePanel from '../comp/SpaceTimePanel';
import { convertLatToStr, convertLonToStr } from '../astro/AstroHelper';
import XQIcon from '../xq-icons';
import {
	STYLE_OPTIONS,
	ACCUM_OPTIONS,
	TENCHING_OPTIONS,
	SEX_OPTIONS,
	ROTATION_OPTIONS,
	calcTaiyi,
	buildTaiyiSnapshotText,
	getStyleLabel,
	getAccumLabel,
} from './TaiYiCalc';

const { Option } = Select;
const { TabPane } = Tabs;
const LAYER2_NUMS = ['二', '七', '六', '一', '八', '三', '四', '九'];
const LAYER3_BRANCH_GUA = ['午', '未', '坤', '申', '酉', '戌', '乾', '亥', '子', '丑', '艮', '寅', '卯', '辰', '巽', '巳'];
// 按 12地支+4卦固定分野（从午位开始顺时针）
// 午大威，子地主
const LAYER4_FIXED = ['大威', '大义', '天道', '大武', '武德', '太簇', '阴主', '阴德', '地主', '阳德', '和德', '吕申', '高丛', '太阳', '大炅', '大神'];
const TAIYI_FONT = '"SimHei", "Heiti SC", "Microsoft YaHei", sans-serif';

class TaiYiMain extends Component {
	constructor(props) {
		super(props);

		this.state = {
			loading: false,
			nongli: null,
			pan: null,
			options: {
				style: 3,
				tn: 0,
				tenching: 0,
				sex: '男',
				rotation: '固定',
			},
		};

		this.unmounted = false;
		this.timeHook = {};
		this.onOptionChange = this.onOptionChange.bind(this);
		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.onTimeChanged = this.onTimeChanged.bind(this);
		this.getTimeFieldsFromSelector = this.getTimeFieldsFromSelector.bind(this);
		this.clickPlot = this.clickPlot.bind(this);
		this.onGenderChange = this.onGenderChange.bind(this);
		this.changeGeo = this.changeGeo.bind(this);
		this.requestNongli = this.requestNongli.bind(this);
		this.genParams = this.genParams.bind(this);
		this.recalc = this.recalc.bind(this);

		if (this.props.hook) {
			this.props.hook.fun = (fields) => {
				if (this.unmounted) {
					return;
				}
				this.requestNongli(fields || this.props.fields);
			};
		}
	}

	componentDidMount() {
		this.unmounted = false;
		if (this.props.fields) {
			this.requestNongli(this.props.fields);
		}
	}

	componentDidUpdate(prevProps) {
		if (prevProps.fields !== this.props.fields && this.props.fields) {
			this.requestNongli(this.props.fields);
		}
	}

	componentWillUnmount() {
		this.unmounted = true;
	}

	onFieldsChange(field) {
		if (this.props.dispatch) {
			const flds = {
				...(this.props.fields || {}),
				...field,
			};
			this.props.dispatch({
				type: 'astro/fetchByFields',
				payload: flds,
			});
		}
	}

	onTimeChanged(value) {
		const dt = value.time;
		this.onFieldsChange({
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
		});
	}

	getTimeFieldsFromSelector(baseFields){
		if(!this.timeHook || !this.timeHook.getValue){
			return null;
		}
		const raw = this.timeHook.getValue();
		const dt = raw && raw.value && raw.value instanceof DateTime
			? raw.value
			: (raw && raw.time && raw.time instanceof DateTime ? raw.time : null);
		if(!dt){
			return null;
		}
		const patch = {
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
		};
		return {
			...(baseFields || {}),
			...patch,
		};
	}

	clickPlot(){
		const nextFields = this.getTimeFieldsFromSelector(this.props.fields) || this.props.fields;
		if(!nextFields){
			return;
		}
		if(nextFields.date && nextFields.time && nextFields.zone){
			this.onFieldsChange({
				date: nextFields.date,
				time: nextFields.time,
				ad: nextFields.ad,
				zone: nextFields.zone,
			});
		}
		this.requestNongli(nextFields);
	}

	onGenderChange(val) {
		this.onOptionChange('sex', val === 0 ? '女' : '男');
		this.onFieldsChange({
			gender: { value: val },
		});
	}

	changeGeo(rec) {
		this.onFieldsChange({
			lon: { value: convertLonToStr(rec.lng) },
			lat: { value: convertLatToStr(rec.lat) },
			gpsLon: { value: rec.gpsLng },
			gpsLat: { value: rec.gpsLat },
		});
	}

	genParams(fields) {
		const flds = fields || this.props.fields;
		if (!flds) {
			return null;
		}
		return {
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm:ss'),
			zone: flds.zone.value,
			lon: flds.lon.value,
			lat: flds.lat.value,
			gpsLat: flds.gpsLat.value,
			gpsLon: flds.gpsLon.value,
			gender: flds.gender.value,
			after23NewDay: 0,
		};
	}

	recalc(fields, nongli, options) {
		const pan = calcTaiyi(fields || this.props.fields, nongli || this.state.nongli, options || this.state.options);
		this.setState({ pan }, () => {
			if (pan) {
				saveModuleAISnapshot('taiyi', buildTaiyiSnapshotText(pan));
			}
		});
	}

	async requestNongli(fields) {
		const params = this.genParams(fields);
		if(!params){
			return;
		}
		const result = await fetchPreciseNongli(params);
		if(!result){
			if(!this.unmounted){
				this.setState({ nongli: null, pan: null, loading: false });
			}
			return;
		}
		setNongliLocalCache(params, result);
		if (this.unmounted) {
			return;
		}
		const pan = calcTaiyi(fields || this.props.fields, result, this.state.options);
		this.setState({
			nongli: result,
			pan,
			loading: false,
		}, () => {
			if (pan) {
				saveModuleAISnapshot('taiyi', buildTaiyiSnapshotText(pan));
			}
		});
	}

	onOptionChange(key, value) {
		const options = {
			...this.state.options,
			[key]: value,
		};
		this.setState({ options }, () => {
			this.recalc(this.props.fields, this.state.nongli, options);
		});
	}

	polarPoint(cx, cy, r, angleDeg) {
		const rad = angleDeg * Math.PI / 180;
		return {
			x: cx + r * Math.cos(rad),
			y: cy + r * Math.sin(rad),
		};
	}

	renderLeft() {
		const pan = this.state.pan;
		if (!pan) {
			return <Card bordered={false}>暂无太乙盘数据</Card>;
		}
		const width = 860;
		const height = 720;
		const centerX = 430;
		const centerY = 360;
		const r0 = 78;
		const r1 = 124;
		const r2 = 172;
		const r3 = 222;
		const r4 = 304;
		const stroke = 'var(--horosa-border-strong, #111)';
		const textColor = 'var(--horosa-text, #111)';
		const textWeight = '500';
			const palaceInfo = {};
			(pan.palaces || []).forEach((p) => {
				palaceInfo[p.palace] = p.items || [];
			});
			const layer5 = LAYER3_BRANCH_GUA.map((p) => (palaceInfo[p] ? palaceInfo[p].slice(0) : []));
			const ganzhiCompact = pan && pan.ganzhi
				? [pan.ganzhi.year || '—', pan.ganzhi.month || '—', pan.ganzhi.day || '—', pan.ganzhi.time || '—'].join('/')
				: '—';
			const topLeftInfo = [
				`农历:${pan.lunarText || '—'}`,
				`真太阳时:${pan.realSunTime || '—'}`,
				`干支:${ganzhiCompact}`,
				`节气:${pan.jiedelta || '—'}`,
			];
			const bottomRightInfo = [
				`积数:${pan.accNum}`,
				`命式:${pan.zhao}`,
				`局:${pan.kook ? pan.kook.text : ''}`,
				`定算:${pan.setCal}`,
				`主算:${pan.homeCal}`,
			`客算:${pan.awayCal}`,
			`太乙数:${pan.taiyiNum}`,
		];
		return (
			<div>
				<Card bordered={false}>
					<div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
						<svg
							viewBox={`0 0 ${width} ${height}`}
							style={{ width: '100%', maxWidth: 860, background: 'transparent', textRendering: 'geometricPrecision' }}
						>
							<circle cx={centerX} cy={centerY} r={r0} fill="none" stroke={stroke} strokeWidth="2.5" />
							<circle cx={centerX} cy={centerY} r={r1} fill="none" stroke={stroke} strokeWidth="2" />
							<circle cx={centerX} cy={centerY} r={r2} fill="none" stroke={stroke} strokeWidth="2" />
							<circle cx={centerX} cy={centerY} r={r3} fill="none" stroke={stroke} strokeWidth="2" />
							<circle cx={centerX} cy={centerY} r={r4} fill="none" stroke={stroke} strokeWidth="2.5" />

								<text
									x={20}
									y={30}
									textAnchor="start"
									dominantBaseline="hanging"
									fill={textColor}
									stroke="none"
									fontSize="15"
									fontWeight={textWeight}
									fontFamily={TAIYI_FONT}
								>
									{topLeftInfo.map((line, lineIdx) => (
										<tspan key={`ty_meta_${lineIdx}`} x={20} dy={lineIdx === 0 ? 0 : 20}>
											{line}
										</tspan>
									))}
								</text>
								<text
									x={width - 20}
									y={height - 20 - ((bottomRightInfo.length - 1) * 20)}
									textAnchor="end"
									dominantBaseline="hanging"
									fill={textColor}
									stroke="none"
									fontSize="15"
									fontWeight={textWeight}
									fontFamily={TAIYI_FONT}
								>
									{bottomRightInfo.map((line, lineIdx) => (
										<tspan key={`ty_meta_bottom_${lineIdx}`} x={width - 20} dy={lineIdx === 0 ? 0 : 20}>
											{line}
										</tspan>
									))}
								</text>

							{LAYER2_NUMS.map((_, idx) => {
								const angle = -112.5 + idx * 45;
								const p1 = this.polarPoint(centerX, centerY, r0, angle);
								const p2 = this.polarPoint(centerX, centerY, r1, angle);
								return (
									<line
										key={`l2_line_${idx}`}
										x1={p1.x}
										y1={p1.y}
										x2={p2.x}
										y2={p2.y}
										stroke={stroke}
										strokeWidth="1.8"
									/>
								);
							})}

							{LAYER3_BRANCH_GUA.map((_, idx) => {
								const angle = -101.25 + idx * 22.5;
								const p1 = this.polarPoint(centerX, centerY, r1, angle);
								const p2 = this.polarPoint(centerX, centerY, r4, angle);
								return (
									<line
										key={`l345_line_${idx}`}
										x1={p1.x}
										y1={p1.y}
										x2={p2.x}
										y2={p2.y}
										stroke={stroke}
										strokeWidth="1.5"
									/>
								);
							})}

								<text
									x={centerX}
									y={centerY - 12}
									textAnchor="middle"
									dominantBaseline="middle"
									fill={textColor}
									stroke="none"
									fontSize="48"
									fontWeight={textWeight}
									fontFamily={TAIYI_FONT}
								>
									五
							</text>
								<text
									x={centerX}
									y={centerY + 30}
									textAnchor="middle"
									dominantBaseline="middle"
									fill={textColor}
									stroke="none"
									fontSize="34"
									fontWeight={textWeight}
									fontFamily={TAIYI_FONT}
								>
									中宫
							</text>

							{LAYER2_NUMS.map((txt, idx) => {
								const angle = -90 + idx * 45;
								const p = this.polarPoint(centerX, centerY, (r0 + r1) / 2, angle);
								return (
									<text
										key={`l2_txt_${txt}_${idx}`}
										x={p.x}
										y={p.y}
										textAnchor="middle"
											dominantBaseline="middle"
											fill={textColor}
											stroke="none"
											fontSize="36"
											fontWeight={textWeight}
											fontFamily={TAIYI_FONT}
										>
											{txt}
									</text>
								);
							})}

							{LAYER3_BRANCH_GUA.map((txt, idx) => {
								const angle = -90 + idx * 22.5;
								const p = this.polarPoint(centerX, centerY, (r1 + r2) / 2, angle);
								return (
									<text
										key={`l3_txt_${txt}_${idx}`}
										x={p.x}
										y={p.y}
										textAnchor="middle"
											dominantBaseline="middle"
											fill={textColor}
											stroke="none"
											fontSize="34"
											fontWeight={textWeight}
											fontFamily={TAIYI_FONT}
										>
											{txt}
									</text>
								);
							})}

							{LAYER4_FIXED.map((txt, idx) => {
								const angle = -90 + idx * 22.5;
								const p = this.polarPoint(centerX, centerY, (r2 + r3) / 2, angle);
								return (
									<text
										key={`l4_txt_${txt}_${idx}`}
										x={p.x}
										y={p.y}
										textAnchor="middle"
											dominantBaseline="middle"
											fill={textColor}
											stroke="none"
											fontSize="23"
											fontWeight={textWeight}
											fontFamily={TAIYI_FONT}
										>
											{txt}
									</text>
								);
							})}

							{layer5.map((lines, idx) => {
								const angle = -90 + idx * 22.5;
								const p = this.polarPoint(centerX, centerY, (r3 + r4) / 2, angle);
								const merged = (lines || []).filter(Boolean).slice(0, 3);
								if (!merged.length) {
									return null;
								}
								return (
									<text
										key={`l5_txt_${idx}`}
										x={p.x}
										y={p.y}
										textAnchor="middle"
											dominantBaseline="middle"
											fill={textColor}
											stroke="none"
											fontSize="16"
											fontWeight={textWeight}
											fontFamily={TAIYI_FONT}
										>
										{merged.map((ln, lnIdx) => (
											<tspan key={`l5_tspan_${idx}_${lnIdx}`} x={p.x} dy={lnIdx === 0 ? 0 : 18}>
												{ln}
											</tspan>
										))}
									</text>
								);
							})}
						</svg>
					</div>
				</Card>
			</div>
		);
	}

	renderInputPanel() {
		const opt = this.state.options;
		const fields = this.props.fields || {};
		let datetm = new DateTime();
		if (fields.date && fields.time) {
			const str = `${fields.date.value.format('YYYY-MM-DD')} ${fields.time.value.format('HH:mm:ss')}`;
			datetm = datetm.parse(str, 'YYYY-MM-DD HH:mm:ss');
			if (fields.zone) {
				datetm.setZone(fields.zone.value);
			}
		}
		return (
			<div className="horosa-taiyi-input-stack">
				<div>
					<div className="horosa-side-panel-title">太乙设置</div>
					<div className="horosa-side-panel-subtitle">时间、地点与起盘选项</div>
				</div>

				<SpaceTimePanel
					fields={fields}
					value={datetm}
					onTimeChange={this.onTimeChanged}
					timeHook={this.timeHook}
					onGeoChange={this.changeGeo}
				/>

				<div className="horosa-taiyi-input-section">
					<div className="horosa-taiyi-field-title"><XQIcon name="taiyi" />盘式选项</div>
					<div className="horosa-taiyi-select-grid">
						<label className="horosa-taiyi-select-field">
							<span>性别</span>
							<Select value={fields.gender ? fields.gender.value : 1} onChange={this.onGenderChange}>
								<Option value={-1}>未知</Option>
								<Option value={0}>女</Option>
								<Option value={1}>男</Option>
							</Select>
						</label>
						<label className="horosa-taiyi-select-field">
							<span>盘式</span>
							<Select value={opt.style} onChange={(v) => this.onOptionChange('style', v)}>
								{STYLE_OPTIONS.map((item) => <Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-taiyi-select-field">
							<span>积年</span>
							<Select value={opt.tn} onChange={(v) => this.onOptionChange('tn', v)}>
								{ACCUM_OPTIONS.map((item) => <Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-taiyi-select-field">
							<span>十精</span>
							<Select value={opt.tenching} onChange={(v) => this.onOptionChange('tenching', v)}>
								{TENCHING_OPTIONS.map((item) => <Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-taiyi-select-field">
							<span>旋转</span>
							<Select value={opt.rotation} onChange={(v) => this.onOptionChange('rotation', v)}>
								{ROTATION_OPTIONS.map((item) => <Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-taiyi-select-field">
							<span>命法</span>
							<Select value={opt.sex} onChange={(v) => this.onOptionChange('sex', v)}>
								{SEX_OPTIONS.map((item) => <Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
					</div>
				</div>

				<div className="horosa-taiyi-action-row">
					<Button type="primary" onClick={this.clickPlot}>起盘</Button>
				</div>
			</div>
		);
	}

	renderInfoRows() {
		const pan = this.state.pan;
		const opt = this.state.options;
		const fields = this.props.fields || {};
		const fieldTime = fields.date && fields.time
			? `${fields.date.value.format('YYYY-MM-DD')} ${fields.time.value.format('HH:mm:ss')}`
			: '—';
		const geo = fields.lon && fields.lat ? `${fields.lon.value} ${fields.lat.value}` : '—';
		const rows = [
			['起盘时间', fieldTime],
			['地点', geo],
			['起盘方式', getStyleLabel(opt.style)],
			['积年方式', getAccumLabel(opt.tn)],
			['太乙', pan ? `${pan.taiyiPalace}宫` : '—'],
			['文昌', pan ? pan.skyeyes : '—'],
			['始击', pan ? pan.sf : '—'],
			['太岁', pan ? pan.taishui : '—'],
			['合神', pan ? pan.hegod : '—'],
			['计神', pan ? pan.jigod : '—'],
			['定目', pan ? (pan.se || '—') : '—'],
			['主大将/参将', pan ? `${pan.homeGeneralPalace || '—'}/${pan.homeVGenPalace || '—'}` : '—'],
			['客大将/参将', pan ? `${pan.awayGeneralPalace || '—'}/${pan.awayVGenPalace || '—'}` : '—'],
			['定大将/参将', pan ? `${pan.setGeneralPalace || '—'}/${pan.setVGenPalace || '—'}` : '—'],
			['君臣民基', pan ? `${pan.kingbase || '—'}/${pan.officerbase || '—'}/${pan.pplbase || '—'}` : '—'],
			['四神/天乙/地乙', pan ? `${pan.fgd || '—'}/${pan.skyyi || '—'}/${pan.earthyi || '—'}` : '—'],
			['直符/飞符', pan ? `${pan.zhifu || '—'}/${pan.flyfu || '—'}` : '—'],
			['五福/帝符/太尊', pan ? `${pan.wufuPalace || '—'}/${pan.kingfu || '—'}/${pan.taijun || '—'}` : '—'],
			['飞鸟', pan ? (pan.flybird || '—') : '—'],
			['三风/五风/八风', pan ? `${pan.threewindPalace || '—'}/${pan.fivewindPalace || '—'}/${pan.eightwindPalace || '—'}` : '—'],
			['大游/小游', pan ? `${pan.bigyoPalace || '—'}/${pan.smyoPalace || '—'}` : '—'],
		];
		return rows.map(([label, value]) => (
			<div className="horosa-taiyi-info-row" key={label}>
				<span>{label}</span>
				<strong>{value}</strong>
			</div>
		));
	}

	renderPalaceRows() {
		const pan = this.state.pan;
		if (!pan || !pan.palace16) {
			return <div className="horosa-taiyi-empty">暂无十六宫数据</div>;
		}
		return pan.palace16.map((item) => (
			<div className="horosa-taiyi-palace-row" key={item.palace}>
				<strong>{item.palace}</strong>
				<span>{(item.items || []).join('、') || '—'}</span>
			</div>
		));
	}

	renderRightPanel() {
		const pan = this.state.pan;
		const snapshot = pan ? buildTaiyiSnapshotText(pan) : '暂无太乙盘数据';
		return (
			<Tabs defaultActiveKey="overview" tabPosition="top" className="horosa-taiyi-tabs">
				<TabPane tab="概览" key="overview">
					<div className="horosa-taiyi-info-card">
						{this.renderInfoRows()}
					</div>
				</TabPane>
				<TabPane tab="十六宫" key="palaces">
					<div className="horosa-taiyi-palace-list">
						{this.renderPalaceRows()}
					</div>
				</TabPane>
				<TabPane tab="快照" key="snapshot">
					<pre className="horosa-taiyi-snapshot">{snapshot}</pre>
				</TabPane>
			</Tabs>
		);
	}

	render() {
		let height = this.props.height ? this.props.height : 760;
		if (height === '100%') {
			height = 760;
		} else {
			height = height - 20;
		}
		return (
			<div className="horosa-taiyi-page horosa-astro-redesign horosa-taiyi-redesign" style={{ height: height, minHeight: height, overflow: 'hidden' }}>
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-taiyi-redesign-layout">
					<Spin spinning={this.state.loading}>
						<div className="horosa-astro-redesign-grid horosa-taiyi-redesign-grid">
							<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-taiyi-input-panel">
								{this.renderInputPanel()}
							</div>
							<div className="horosa-chart-stage horosa-chart-stage-redesign horosa-taiyi-chart-panel xq-chart-renderer xq-chart-renderer-taiyi">
								<div className="horosa-taiyi-board-host">
									{this.renderLeft()}
								</div>
							</div>
							<div className="horosa-inspector-panel horosa-astro-content-panel horosa-taiyi-info-panel">
								<div className="horosa-side-panel-heading horosa-taiyi-info-heading">
									<div>
										<div className="horosa-side-panel-title">太乙信息</div>
										<div className="horosa-side-panel-subtitle">概览、十六宫与快照</div>
									</div>
								</div>
								{this.renderRightPanel()}
							</div>
						</div>
					</Spin>
					<div className="horosa-bottom-quick-dock horosa-taiyi-quick-dock">
						<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
						<div className="horosa-bottom-quick-actions horosa-taiyi-quick-placeholders">
							{Array.from({ length: 8 }).map((_, idx) => (
								<div className="horosa-bottom-quick-placeholder" key={idx} />
							))}
						</div>
					</div>
				</div>
			</div>
		);
	}
}

export default TaiYiMain;
