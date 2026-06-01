import { Component } from 'react';
import { message, Spin } from 'antd';
import { XQButton as Button, XQSelect as Select, XQTabs as Tabs } from '../xq-ui';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import { fetchPreciseNongli } from '../../utils/preciseCalcBridge';
import GeoCoordModal from '../amap/GeoCoordModal';
import PlusMinusTime from '../astro/PlusMinusTime';
import DateTime from '../comp/DateTime';
import SpaceTimePanel from '../comp/SpaceTimePanel';
import { convertLatToStr, convertLonToStr } from '../astro/AstroHelper';
import { resolveGeoZone } from '../../utils/timezone';
import XQIcon from '../xq-icons';
import {
	STYLE_OPTIONS,
	METHOD_OPTIONS,
	TIME_BASIS_OPTIONS,
	DAY_SWITCH_OPTIONS,
	GAME_THEORY_OPTIONS,
	fetchTaiyiPan,
	buildTaiyiSnapshotText,
	getStyleLabel,
	getMethodLabel,
	getMethodSource,
} from './TaiYiCalc';
import { openKentangCaseDrawer, getKentangSavedCasePayload } from '../../utils/kentangCaseSave';
import { defaultAfter23NewDay, defaultLateZiHourUseNextDay } from '../../utils/dayBoundary';

const { Option } = Select;
const { TabPane } = Tabs;
const LAYER2_NUMS = ['二', '七', '六', '一', '八', '三', '四', '九'];
const LAYER3_BRANCH_GUA = ['午', '未', '坤', '申', '酉', '戌', '乾', '亥', '子', '丑', '艮', '寅', '卯', '辰', '巽', '巳'];
// 按 12地支+4卦固定分野（从午位开始顺时针）
// 午大威，子地主
const LAYER4_FIXED = ['大威', '大义', '天道', '大武', '武德', '太簇', '阴主', '阴德', '地主', '阳德', '和德', '吕申', '高丛', '太阳', '大炅', '大神'];
const TAIYI_FONT = '"SimHei", "Heiti SC", "Microsoft YaHei", sans-serif';
const PRECISE_NONGLI_TIMEOUT_MS = 3500;

function withTimeout(promise, timeoutMs) {
	return Promise.race([
		promise,
		new Promise((resolve) => {
			setTimeout(() => resolve(null), timeoutMs);
		}),
	]);
}

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
				sex: '男',
				timeBasis: 'direct',
				after23NewDay: defaultAfter23NewDay(),
				lateZiHourUseNextDay: defaultLateZiHourUseNextDay(),
				gameTheory: 0,
			},
			rightPanelTab: 'overview',
		};

		this.unmounted = false;
		this.timeHook = {};
		this.taiyiRequestSeq = 0;
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
		this.restoreFromCurrentCase = this.restoreFromCurrentCase.bind(this);
		this.clickSaveCase = this.clickSaveCase.bind(this);
		this.setRightPanelTab = this.setRightPanelTab.bind(this);
		this.navigateFeature = this.navigateFeature.bind(this);

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
		this._after23BoundaryUserOverrode = false; // 用户拍板:左栏改过 after23NewDay 后,全局事件不再覆盖
		this._lateZiHourUserOverrode = false; // v2.2.1: 同款时柱开关局部覆盖语义
		if(typeof window !== 'undefined'){
			this._dayBoundaryListener = (ev) => {
				if(this._after23BoundaryUserOverrode) return;
				const v = ev && ev.detail ? ev.detail.after23NewDay : null;
				if((v === 0 || v === 1) && typeof this.onOptionChange === 'function'){
					this.onOptionChange('after23NewDay', v, { fromGlobal: true });
				}
			};
			window.addEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
			this._lateZiHourListener = (ev) => {
				if(this._lateZiHourUserOverrode) return;
				const v = ev && ev.detail ? ev.detail.lateZiHourUseNextDay : null;
				if((v === 0 || v === 1) && typeof this.onOptionChange === 'function'){
					this.onOptionChange('lateZiHourUseNextDay', v, { fromGlobal: true });
				}
			};
			window.addEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
		}
		if (this.restoreFromCurrentCase(true)) {
			return;
		}
		if (this.props.fields) {
			this.requestNongli(this.props.fields);
		}
	}

	componentDidUpdate(prevProps) {
		if (prevProps.fields !== this.props.fields && this.props.fields) {
			if (this.restoreFromCurrentCase(false)) {
				return;
			}
			this.requestNongli(this.props.fields);
		}
	}

	componentWillUnmount() {
		this.unmounted = true;
		if(typeof window !== 'undefined' && this._dayBoundaryListener){
			window.removeEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
		}
		if(typeof window !== 'undefined' && this._lateZiHourListener){
			window.removeEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
		}
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
		const payload = {
			lon: { value: convertLonToStr(rec.lng) },
			lat: { value: convertLatToStr(rec.lat) },
			gpsLon: { value: rec.gpsLng },
			gpsLat: { value: rec.gpsLat },
		};
		// 选地点 → 时区自动校正 + 重锚 date/time 到新时区(clone+setZone:保留钟面时刻、瞬时随之偏移);
		// 否则排盘仍用 date 实例残留的旧时区算瞬时/真太阳时。手动改过时区则沿用 rec.zone。
		const f = this.props.fields || {};
		const dDt = f.date && f.date.value;
		const tDt = f.time && f.time.value;
		const ds = (dDt && dDt.format) ? dDt.format('YYYY-MM-DD') : null;
		const z = resolveGeoZone(rec, ds);
		if(z){
			payload.zone = { value: z };
			if(dDt && dDt.clone){ const nd = dDt.clone(); nd.setZone(z); payload.date = { value: nd }; payload.ad = { value: nd.ad }; }
			if(tDt && tDt.clone){ const nt = tDt.clone(); nt.setZone(z); payload.time = { value: nt }; }
		}
		this.onFieldsChange(payload);
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
			after23NewDay: this.state.options.after23NewDay || 0,
		};
	}

	async recalc(fields, nongli, options) {
		const reqSeq = ++this.taiyiRequestSeq;
		const nextFields = fields || this.props.fields;
		const nextNongli = nongli || this.state.nongli;
		const nextOptions = options || this.state.options;
		if(!nextFields){
			return;
		}
		this.setState({ loading: true });
		let pan = null;
		try{
			pan = await fetchTaiyiPan(nextFields, nextNongli, nextOptions);
		}catch(e){
			console.warn('kintaiyi backend failed', e);
			pan = null;
			if(!this.unmounted && reqSeq === this.taiyiRequestSeq){
				message.error('太乙计算失败：本地太乙服务不可用');
			}
		}
		if(this.unmounted || reqSeq !== this.taiyiRequestSeq){
			return;
		}
		this.setState({ pan, loading: false }, () => {
			if (pan) {
				saveModuleAISnapshot('taiyi', buildTaiyiSnapshotText(pan));
			}
		});
	}

	setRightPanelTab(key) {
		this.setState({
			rightPanelTab: key,
		});
	}

	navigateFeature(tabKey, subTab) {
		if (this.props.dispatch) {
			const payload = {
				currentTab: tabKey,
			};
			if (subTab) {
				payload.currentSubTab = subTab;
			}
			this.props.dispatch({
				type: 'astro/save',
				payload,
			});
		}
	}

	async requestNongli(fields) {
		const params = this.genParams(fields);
		if(!params){
			return;
		}
		this.setState({ loading: true });
		if (this.unmounted) {
			return;
		}
		let nongli = null;
		try {
			nongli = await withTimeout(fetchPreciseNongli(params), PRECISE_NONGLI_TIMEOUT_MS);
		} catch (e) {
			console.warn('taiyi precise nongli failed, continuing with kintaiyi calendar fields', e);
		}
		if (this.unmounted) {
			return;
		}
		this.setState({ nongli });
		await this.recalc(fields || this.props.fields, nongli, this.state.options);
	}

	onOptionChange(key, value, opts) {
		// 用户拍板: 左栏改过 after23NewDay 后,全局事件不再覆盖。fromGlobal 时不打标记。
		if(key === 'after23NewDay' && !(opts && opts.fromGlobal)){
			this._after23BoundaryUserOverrode = true;
		}
		const options = {
			...this.state.options,
			[key]: value,
		};
		this.setState({ options }, () => {
			this.recalc(this.props.fields, this.state.nongli, options);
		});
	}

	restoreFromCurrentCase(force) {
		const saved = getKentangSavedCasePayload('taiyi');
		if (!saved || !saved.payload) {
			return false;
		}
		if (!force && this.lastRestoredCaseId === saved.caseVersion) {
			return false;
		}
		const payload = saved.payload;
		const options = payload.options && typeof payload.options === 'object' ? payload.options : {};
		this.lastRestoredCaseId = saved.caseVersion;
		this.taiyiRequestSeq += 1;
		this.setState({
			loading: false,
			options: {
				...this.state.options,
				...options,
			},
			nongli: payload.nongli || null,
			pan: payload.pan || null,
			rightPanelTab: 'overview',
		}, () => {
			if (this.state.pan) {
				saveModuleAISnapshot('taiyi', buildTaiyiSnapshotText(this.state.pan));
			}
		});
		return true;
	}

	clickSaveCase() {
		if (!this.state.pan) {
			message.warning('请先起盘后再保存');
			return;
		}
		openKentangCaseDrawer({
			dispatch: this.props.dispatch,
			fields: this.props.fields,
			module: 'taiyi',
			label: '太乙',
			payload: {
				options: this.state.options,
				nongli: this.state.nongli,
				pan: this.state.pan,
				snapshot: buildTaiyiSnapshotText(this.state.pan),
			},
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
			return <div className="horosa-taiyi-empty horosa-taiyi-board-empty">暂无太乙盘数据</div>;
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
			const pillars = pan && pan.ganzhi ? pan.ganzhi : {};
			const panOptions = pan && pan.options ? pan.options : {};
			const topLeftInfo = [
				`农历：${pan.lunarText || '—'}`,
				`直接时间：${pan.clockTime || '—'}　真太阳时：${pan.realSunTime || '—'}`,
				`年柱：${pillars.year || '—'}　月柱：${pillars.month || '—'}`,
				`日柱：${pillars.day || '—'}　时柱：${pillars.time || '—'}`,
				`节气：${pan.jiedelta || '—'}`,
				`计法：${panOptions.styleLabel || '—'}　古法：${panOptions.methodLabel || panOptions.accumLabel || '—'}`,
				`年号：${pan.reignYear || this.getSectionValue('年號')}`,
				`纪元：${pan.calendarEra || pan.jiyuan || this.getSectionValue('紀元')}`,
			];
			const topMetaX = 14;
			const topMetaY = 4;
			const topMetaLineHeight = 17;
			const topMetaFontSize = 13;
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
			<div className="horosa-taiyi-board-canvas">
					<div className="horosa-taiyi-board-svg-wrap">
						<svg
							className="horosa-taiyi-board-svg"
							viewBox={`0 0 ${width} ${height}`}
							preserveAspectRatio="xMidYMid meet"
							style={{ background: 'transparent', textRendering: 'geometricPrecision' }}
						>
							<circle cx={centerX} cy={centerY} r={r0} fill="none" stroke={stroke} strokeWidth="2.5" />
							<circle cx={centerX} cy={centerY} r={r1} fill="none" stroke={stroke} strokeWidth="2" />
							<circle cx={centerX} cy={centerY} r={r2} fill="none" stroke={stroke} strokeWidth="2" />
							<circle cx={centerX} cy={centerY} r={r3} fill="none" stroke={stroke} strokeWidth="2" />
							<circle cx={centerX} cy={centerY} r={r4} fill="none" stroke={stroke} strokeWidth="2.5" />

								<text
									x={topMetaX}
									y={topMetaY}
									textAnchor="start"
									dominantBaseline="hanging"
									fill={textColor}
									stroke="none"
									fontSize={topMetaFontSize}
									fontWeight={textWeight}
									fontFamily={TAIYI_FONT}
								>
									{topLeftInfo.map((line, lineIdx) => (
										<tspan key={`ty_meta_${lineIdx}`} x={topMetaX} dy={lineIdx === 0 ? 0 : topMetaLineHeight}>
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
								const fontSize = merged.length >= 3 ? 14 : (merged.length === 2 ? 15 : 16);
								const lineHeight = merged.length >= 3 ? 16 : 17;
								const firstDy = -((merged.length - 1) * lineHeight) / 2;
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
											fontSize={fontSize}
											fontWeight={textWeight}
											fontFamily={TAIYI_FONT}
										>
										{merged.map((ln, lnIdx) => (
											<tspan key={`l5_tspan_${idx}_${lnIdx}`} x={p.x} dy={lnIdx === 0 ? firstDy : lineHeight}>
												{ln}
											</tspan>
										))}
									</text>
								);
							})}
						</svg>
					</div>
			</div>
		);
	}

	renderInputPanel() {
		const opt = this.state.options;
		const fields = this.props.fields || {};
		const isLifeStyle = opt.style === 5;
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
							<span>{isLifeStyle ? '命法性别' : '性别'}</span>
							<Select value={isLifeStyle ? (opt.sex === '女' ? 0 : 1) : (fields.gender ? fields.gender.value : 1)} onChange={this.onGenderChange}>
								{!isLifeStyle && <Option value={-1}>未知</Option>}
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
						{!isLifeStyle && (
							<label className="horosa-taiyi-select-field">
								<span>古法公式</span>
								<Select value={opt.tn} onChange={(v) => this.onOptionChange('tn', v)}>
									{METHOD_OPTIONS.map((item) => <Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</label>
						)}
						<label className="horosa-taiyi-select-field">
							<span>时间基准</span>
							<Select value={opt.timeBasis} onChange={(v) => this.onOptionChange('timeBasis', v)}>
								{TIME_BASIS_OPTIONS.map((item) => <Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-taiyi-select-field">
							<span>换日</span>
							<Select value={opt.after23NewDay} onChange={(v) => this.onOptionChange('after23NewDay', v)}>
								{DAY_SWITCH_OPTIONS.map((item) => <Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						{!isLifeStyle && (
							<label className="horosa-taiyi-select-field">
								<span>博弈</span>
								<Select value={opt.gameTheory} onChange={(v) => this.onOptionChange('gameTheory', v)}>
									{GAME_THEORY_OPTIONS.map((item) => <Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</label>
						)}
					</div>
				</div>

				<div className="horosa-taiyi-action-row">
					<Button type="primary" onClick={this.clickPlot}>起盘</Button>
					<Button onClick={this.clickSaveCase}>保存</Button>
				</div>
			</div>
		);
	}

	renderInfoRows() {
		const pan = this.state.pan;
		const opt = this.state.options;
		const fields = this.props.fields || {};
		const panOptions = pan && pan.options ? pan.options : {};
		const isLifeStyle = opt.style === 5;
		const fieldTime = fields.date && fields.time
			? `${fields.date.value.format('YYYY-MM-DD')} ${fields.time.value.format('HH:mm:ss')}`
			: '—';
		const geo = fields.lon && fields.lat ? `${fields.lon.value} ${fields.lat.value}` : '—';
		const rows = [
			['起盘时间', fieldTime],
			['直接时间', pan ? (pan.clockTime || '—') : '—'],
			['真太阳时', pan ? (pan.realSunTime || '—') : '—'],
			['地点', geo],
			['起盘方式', panOptions.styleLabel || getStyleLabel(opt.style)],
			['历史年号', pan ? (pan.reignYear || this.getSectionValue('年號')) : '—'],
			['太乙纪元', pan ? (pan.calendarEra || pan.jiyuan || this.getSectionValue('紀元')) : '—'],
			['时间基准', panOptions.timeBasisLabel || '直接时间'],
			['换日', panOptions.daySwitchLabel || '23点算第二天'],
		];
		if (isLifeStyle) {
			rows.push(
				['性别', panOptions.sexLabel || opt.sex || '—'],
				['命局', this.getSectionValue('命局', pan && pan.kook ? pan.kook.text : '—')],
				['命宫/身宫', `${this.getSectionValue('安命宮')}/${this.getSectionValue('安身宮')}`],
				['飞禄/飞马', `${this.getSectionValue('飛祿')}/${this.getSectionValue('飛馬')}`],
				['黑符', this.getSectionValue('黑符')],
				['阳九/百六', `${this.getSectionValue('陽九')}/${this.getSectionValue('百六')}`],
				['阳九行限', this.getSectionValue('陽九行限')],
				['百六行限', this.getSectionValue('百六行限')]
			);
		} else {
			rows.push(
				['古法公式', panOptions.methodLabel || panOptions.accumLabel || getMethodLabel(opt.tn)],
				['古法出处', panOptions.methodSource || getMethodSource(opt.tn)],
				['博弈', panOptions.gameTheoryLabel || (opt.gameTheory === 1 ? '开启' : '关闭')],
				['局式', pan ? (pan.kook && pan.kook.text ? pan.kook.text : '—') : '—'],
				['阳九/百六', `${this.getSectionValue('陽九')}/${this.getSectionValue('百六')}`],
				['太乙', pan ? `${pan.taiyiPalace || '—'}宫` : '—'],
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
				['三风/五风/八风', pan ? `${this.formatWindValue('threewind')}/${this.formatWindValue('fivewind')}/${this.formatWindValue('eightwind')}` : '—'],
				['大游/小游', pan ? `${this.formatWindValue('bigyo')}/${this.formatWindValue('smyo')}` : '—']
			);
		}
		return rows.map(([label, value]) => (
			<div className="horosa-taiyi-info-row" key={label}>
				<span>{label}</span>
				<strong>{value}</strong>
			</div>
		));
	}

	formatWindValue(prefix) {
		const pan = this.state.pan;
		if (!pan) {
			return '—';
		}
		const palaceKey = `${prefix}Palace`;
		const numKey = `${prefix}Num`;
		const palace = pan[palaceKey] || '—';
		const num = pan[numKey];
		return num ? `${palace}(${num})` : palace;
	}

	getSectionValue(sourceKey, fallback = '—') {
		const pan = this.state.pan;
		const sections = pan && pan.sections ? pan.sections : [];
		for (let i = 0; i < sections.length; i += 1) {
			const rows = sections[i].rows || [];
			for (let j = 0; j < rows.length; j += 1) {
				if (rows[j].sourceKey === sourceKey || rows[j].label === sourceKey) {
					return this.formatDisplayValue(rows[j].value);
				}
			}
		}
		return fallback;
	}

	hasSectionTitles(titles) {
		const pan = this.state.pan;
		const sections = pan && pan.sections ? pan.sections : [];
		const titleSet = new Set(titles);
		return sections.some((section) => titleSet.has(section.title));
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

	formatDisplayValue(value) {
		if (value === undefined || value === null || value === '') {
			return '—';
		}
		if (Array.isArray(value)) {
			return value.map((item) => this.formatDisplayValue(item)).filter((item) => item && item !== '—').join('、') || '—';
		}
		if (typeof value === 'object') {
			const text = Object.keys(value).map((key) => {
				const item = this.formatDisplayValue(value[key]);
				if (!item || item === '—') {
					return '';
				}
				return `${key}：${item}`;
			}).filter(Boolean).join('；');
			return text || '—';
		}
		return `${value}`.replace(/得None/g, '未得').replace(/None/g, '未得');
	}

	renderSectionRows(titles) {
		const pan = this.state.pan;
		const sections = pan && pan.sections ? pan.sections : [];
		const titleSet = titles && titles.length ? new Set(titles) : null;
		const filtered = titleSet ? sections.filter((section) => titleSet.has(section.title)) : sections;
		if (!filtered.length) {
			return <div className="horosa-taiyi-empty">暂无 kintaiyi 输出</div>;
		}
		return filtered.map((section) => (
			<div className="horosa-taiyi-info-card horosa-taiyi-section-card" key={section.title}>
				<div className="horosa-taiyi-info-heading">{section.title}</div>
				{(section.rows || []).map((row) => (
					<div className="horosa-taiyi-info-row" key={`${section.title}_${row.label}`}>
						<span>{row.label}</span>
						<strong>{this.formatDisplayValue(row.value)}</strong>
					</div>
				))}
			</div>
		));
	}

	renderRightPanel() {
		const pan = this.state.pan;
		const showLifeTab = this.hasSectionTitles(['命法', '命宫行限']);
		const showDoorsTab = this.hasSectionTitles(['八门与宿曜']);
		const showRulingsTab = this.hasSectionTitles(['断法', '七大兵法', '博弈']);
		const tabKeys = ['overview', 'palaces', 'spirits'];
		if (showDoorsTab) {
			tabKeys.push('doors');
		}
		if (showRulingsTab) {
			tabKeys.push('rulings');
		}
		if (showLifeTab) {
			tabKeys.push('life');
		}
		const activeKey = tabKeys.indexOf(this.state.rightPanelTab) >= 0 ? this.state.rightPanelTab : 'overview';
		return (
			<Tabs activeKey={activeKey} onChange={this.setRightPanelTab} defaultActiveKey="overview" tabPosition="top" className="horosa-taiyi-tabs">
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
				<TabPane tab="神煞" key="spirits">
					<div className="horosa-taiyi-section-list">
						{this.renderSectionRows(['太乙诸神', '风游', '十二神'])}
					</div>
				</TabPane>
				{showDoorsTab && (
					<TabPane tab="八门" key="doors">
						<div className="horosa-taiyi-section-list">
							{this.renderSectionRows(['八门与宿曜'])}
						</div>
					</TabPane>
				)}
				{showRulingsTab && (
					<TabPane tab="断法" key="rulings">
						<div className="horosa-taiyi-section-list">
							{this.renderSectionRows(['断法', '七大兵法', '博弈'])}
						</div>
					</TabPane>
				)}
				{showLifeTab && (
					<TabPane tab="命法" key="life">
						<div className="horosa-taiyi-section-list">
							{this.renderSectionRows(['命法', '命宫行限'])}
						</div>
					</TabPane>
				)}
			</Tabs>
		);
	}

	renderBottomQuickDock() {
		const showLifeTab = this.hasSectionTitles(['命法', '命宫行限']);
		const showDoorsTab = this.hasSectionTitles(['八门与宿曜']);
		const showRulingsTab = this.hasSectionTitles(['断法', '七大兵法', '博弈']);
		const actions = [
			{ label: '起盘', icon: 'quickPrimary', onClick: this.clickPlot },
			{ label: '保存', icon: 'quickNote', onClick: this.clickSaveCase },
			{ label: '概览', icon: 'quickComposite', active: this.state.rightPanelTab === 'overview', onClick: () => this.setRightPanelTab('overview') },
			{ label: '十六宫', icon: 'quickTransit', active: this.state.rightPanelTab === 'palaces', onClick: () => this.setRightPanelTab('palaces') },
			{ label: '神煞', icon: 'quickReturn', active: this.state.rightPanelTab === 'spirits', onClick: () => this.setRightPanelTab('spirits') },
			...(showDoorsTab ? [{ label: '八门', icon: 'quickNote', active: this.state.rightPanelTab === 'doors', onClick: () => this.setRightPanelTab('doors') }] : []),
			...(showRulingsTab ? [{ label: '断法', icon: 'quickReturn', active: this.state.rightPanelTab === 'rulings', onClick: () => this.setRightPanelTab('rulings') }] : []),
			...(showLifeTab ? [{ label: '命法', icon: 'quickNote', active: this.state.rightPanelTab === 'life', onClick: () => this.setRightPanelTab('life') }] : []),
			{ label: 'AI助手', icon: 'quickAi', onClick: () => this.navigateFeature('aianalysis') },
		].slice(0, 9);
		return (
			<div className="horosa-bottom-quick-dock horosa-taiyi-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-taiyi-quick-actions">
					{actions.map((item) => (
						<button
							type="button"
							key={item.label}
							className={`horosa-bottom-quick-button horosa-taiyi-quick-button${item.active ? ' is-active' : ''}`}
							onClick={item.onClick}
						>
							<span className="horosa-bottom-quick-icon"><XQIcon name={item.icon} /></span>
							<span>{item.label}</span>
						</button>
					))}
				</div>
			</div>
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
										<div className="horosa-side-panel-subtitle">概览、十六宫与神煞</div>
									</div>
								</div>
								{this.renderRightPanel()}
							</div>
						</div>
					</Spin>
					{this.renderBottomQuickDock()}
				</div>
			</div>
		);
	}
}

export default TaiYiMain;
