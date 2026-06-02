import { Component } from 'react';
import { Row, Col, Select, Switch, Slider, Tree, Card, Radio, DatePicker, InputNumber } from 'antd';
import request from '../../utils/request';
import * as Constants from '../../utils/constants';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import UranianDial from './UranianDial';
import UranianModulusDial from './UranianModulusDial';
import { midpointTree } from '../../utils/uranianDial';
import { getStoredUranianDisplay, saveUranianDisplay, URANIAN_DIAL_BASES, dialBaseLabel } from './UranianDialStyle';

const Option = Select.Option;

const DIAL_BODY_IDS = new Set([
	AstroConst.SUN, AstroConst.MOON, AstroConst.MERCURY, AstroConst.VENUS, AstroConst.MARS,
	AstroConst.JUPITER, AstroConst.SATURN, AstroConst.URANUS, AstroConst.NEPTUNE, AstroConst.PLUTO,
	AstroConst.NORTH_NODE, AstroConst.SOUTH_NODE, AstroConst.ASC, AstroConst.MC,
]);

// 个人点 / Basic Six（日月 + Asc/MC + 南北交 + 白羊点）——扫描器默认只围绕这些展开（spec §5.5）。
const PERSONAL_POINTS = new Set([
	AstroConst.SUN, AstroConst.MOON, AstroConst.ASC, AstroConst.MC,
	AstroConst.NORTH_NODE, AstroConst.SOUTH_NODE, AstroConst.ARIES_POINT,
]);

function sunLon(chartRoot){
	const inner = (chartRoot && chartRoot.chart) ? chartRoot.chart : (chartRoot || {});
	const o = (inner.objects || []).find((x) => x.id === AstroConst.SUN);
	return o && Number.isFinite(Number(o.lon)) ? Number(o.lon) : null;
}

function msg(id){ return AstroText.AstroMsgCN[id] || AstroText.AstroTxtMsg[id] || id; }
const pad = (n) => (n < 10 ? '0' + n : '' + n);

// DateTime 无 valueOf()（之前导致太阳弧/年龄算成 NaN）；从 jdn(儒略日，JD2440587.5=Unix纪元) 取毫秒时间戳。
function birthEpochMs(birth){
	const jdn = birth ? Number(birth.jdn) : NaN;
	if (!Number.isFinite(jdn) || jdn === 0) return NaN;
	return (jdn - 2440587.5) * 86400000;
}

// 右栏因子用字形（与盘一致，hover 显名）：TNP=缩写；白羊点=全站 Aries 字形；其余=AstroMsg+AstroChartFont。
function glyphOf(id){
	const tnp = AstroText.isUranian(id) && id !== AstroConst.ARIES_POINT;
	if (tnp) return <span style={{ fontWeight: 600, letterSpacing: '0.3px' }} title={msg(id)}>{AstroText.uranianGlyph(id)}</span>;
	const ch = id === AstroConst.ARIES_POINT ? AstroText.AstroMsg[AstroConst.ARIES] : AstroText.AstroMsg[id];
	if (ch) return <span style={{ fontFamily: AstroConst.AstroChartFont }} title={msg(id)}>{ch}</span>;
	return <span>{msg(id)}</span>;
}

// 安全取 field 值（field 缺失/未填时返回 undefined，绝不抛错）。
function fv(fields, key){
	const f = fields && fields[key];
	return f ? f.value : undefined;
}
function fmt(val, pattern){
	return (val && typeof val.format === 'function') ? val.format(pattern) : undefined;
}

// 一律先校验再发请求：缺/空的 date/time/zone/lat/lon 会让后端 PerChart→GeoPos/Datetime 抛错、
// 回 {err:'param error'}，而 request() 即便 silent 仍会对抛错弹 message.error 提示——故宁可前端拦下不发。
function dialParamsError(p){
	if (!p) return '请先完善出生信息';
	const need = ['date', 'time', 'zone', 'lat', 'lon'];
	for (const k of need){
		const v = p[k];
		if (v === undefined || v === null || `${v}`.trim() === '') return '请先设置出生日期/时间与经纬度';
	}
	return null;
}

function fieldsToParams(fields){
	if (!fields) return null;
	return {
		date: fmt(fv(fields, 'date'), 'YYYY/MM/DD'), time: fmt(fv(fields, 'time'), 'HH:mm:ss'),
		zone: fv(fields, 'zone'), lat: fv(fields, 'lat'), lon: fv(fields, 'lon'),
		gpsLat: fv(fields, 'gpsLat'), gpsLon: fv(fields, 'gpsLon'),
		hsys: fv(fields, 'hsys'), zodiacal: fv(fields, 'zodiacal'), tradition: false, predictive: 0,
		name: fv(fields, 'name') || '', pos: fv(fields, 'pos') || '',
	};
}

// 从盘对象（本命/行运同形）取参与点：行星+三王+北交南交+Asc/MC。
function chartToPoints(chartRoot){
	const inner = (chartRoot && chartRoot.chart) ? chartRoot.chart : (chartRoot || {});
	const out = []; const seen = new Set();
	const push = (id, lon) => { if (id && Number.isFinite(Number(lon)) && !seen.has(id)) { out.push({ id, lon: Number(lon) }); seen.add(id); } };
	(inner.objects || []).forEach((o) => { if (DIAL_BODY_IDS.has(o.id)) push(o.id, o.lon); });
	(inner.angles || []).forEach((o) => { if (DIAL_BODY_IDS.has(o.id)) push(o.id, o.lon); });
	return out;
}

// 全链路 TNP 过滤：showTnp=false 时一并从盘绘制+指针读数+中点树剔除（用户验收口径,2026-06-02）。
function filterByTnp(points, showTnp){
	if (showTnp) return points;
	return (points || []).filter((p) => !AstroText.isUranian(p.id) || p.id === AstroConst.ARIES_POINT);
}

// 数字解析：空串/非数→null（视为「跟本命同地点」）。
function parseNum(v){
	if (v === undefined || v === null || v === '') return null;
	const n = Number(v);
	return Number.isFinite(n) ? n : null;
}

export default class UranianDialMain extends Component {
	constructor(props){
		super(props);
		const disp = getStoredUranianDisplay();
		this.state = {
			...disp,
			showTransit: disp.showTransit || false,
			showSolarArc: disp.showSolarArc || false,
			onlyPersonal: disp.onlyPersonal === undefined ? true : disp.onlyPersonal,
			natalTnp: [],
			transitPoints: null,
			readout: [],
			dataNote: null,        // 出生信息不全时的友好提示（取代裸 param error）
			dialStyle: disp.dialStyle === 'modulus' ? 'modulus' : 'folded', // 盘式：折叠盘 / 多环模数盘
			saArcDirected: 0,      // 太阳弧环被拖动的定向弧(黄道度)
			saAge: 0,              // 由定向弧按 saKey 反推的年龄
			saKey: disp.saKey === 'oneDeg' ? 'oneDeg' : 'naibod', // 太阳弧换算：Naibod / 1°每年
			transitTime: null,     // 行运时刻(null=此刻)，可调
			// 行运/SA 地点可调(null=同本命)。SA 一般地心黄经无需地点,但允许覆盖以方便 relocated 想法。
			transitLat: null, transitLon: null,
			saLat: null, saLon: null,
		};
		this.unmounted = false;
		this.requestNatalTnp = this.requestNatalTnp.bind(this);
		this.requestTransit = this.requestTransit.bind(this);
		this.onReadout = this.onReadout.bind(this);
		this.onSaArc = this.onSaArc.bind(this);
		if (this.props.hook) this.props.hook.fun = () => { if (!this.unmounted) { this.requestNatalTnp(); if (this.state.showTransit) this.requestTransit(); } };
	}

	componentDidMount(){ this.unmounted = false; this.requestNatalTnp(); if (this.state.showTransit) this.requestTransit(); }
	componentWillUnmount(){ this.unmounted = true; }
	componentDidUpdate(prev, prevState){
		if (prev.fields !== this.props.fields) {
			// 改本命 → 拨回默认地点(null=同本命),否则用旧本命的覆盖坐标算新本命的行运,误导。
			this.setState({ saArcDirected: 0, saAge: 0, transitLat: null, transitLon: null, saLat: null, saLon: null });
			this.requestNatalTnp();
			if (this.state.showTransit) this.requestTransit();
		}
		// TNP 关 → 即时裁剪现有 readout(否则上次拖动留下的 TNP 行还在;中点树由 render 即时重算,无需处理)。
		if (prevState && prevState.showTnp !== this.state.showTnp && !this.state.showTnp){
			const isTnp = (id) => AstroText.isUranian(id) && id !== AstroConst.ARIES_POINT;
			const filtered = (this.state.readout || []).filter((h) => {
				if (h.kind === 'body') return !isTnp(h.id);
				return !isTnp(h.a) && !isTnp(h.b);
			});
			if (filtered.length !== (this.state.readout || []).length) this.setState({ readout: filtered });
		}
	}
	toggleSolarArc(v){ this.saveDisp({ showSolarArc: v }); }

	async requestNatalTnp(){
		const params = fieldsToParams(this.props.fields);
		const perr = dialParamsError(params);
		if (perr) { if (!this.unmounted) this.setState({ dataNote: perr }); return; }
		if (!this.unmounted && this.state.dataNote) this.setState({ dataNote: null });
		try {
			const data = await request(`${Constants.ServerRoot}/germany/midpoint`, { body: JSON.stringify(params), silent: true });
			const result = data && data[Constants.ResultKey] ? data[Constants.ResultKey] : null;
			if (!this.unmounted && result && Array.isArray(result.tnp)) this.setState({ natalTnp: result.tnp });
		} catch (e) { /* 静默 */ }
	}

	async requestTransit(){
		const base = fieldsToParams(this.props.fields);
		if (dialParamsError(base)) return; // 缺出生地经纬度等 → 不发 transit /chart，避免 param error 提示
		// 行运时刻可调：state.transitTime(moment)优先，否则此刻。
		const tt = this.state.transitTime;
		const dstr = tt ? tt.format('YYYY/MM/DD') : (() => { const n = new Date(); return `${n.getFullYear()}/${pad(n.getMonth() + 1)}/${pad(n.getDate())}`; })();
		const tstr = tt ? tt.format('HH:mm:ss') : (() => { const n = new Date(); return `${pad(n.getHours())}:${pad(n.getMinutes())}:00`; })();
		// 行运地点可调：null=同本命；显式数字才覆盖（relocated transit）。
		const overrideLat = this.state.transitLat, overrideLon = this.state.transitLon;
		const loc = (overrideLat != null && overrideLon != null) ? { lat: overrideLat, lon: overrideLon, gpsLat: overrideLat, gpsLon: overrideLon } : {};
		const params = { ...base, ...loc, date: dstr, time: tstr };
		try {
			const [chartData, mpData] = await Promise.all([
				request(`${Constants.ServerRoot}/chart`, { body: JSON.stringify({ ...params, cid: null }), silent: true }),
				request(`${Constants.ServerRoot}/germany/midpoint`, { body: JSON.stringify(params), silent: true }),
			]);
			const chartObj = chartData && chartData[Constants.ResultKey] ? chartData[Constants.ResultKey] : null;
			const mp = mpData && mpData[Constants.ResultKey] ? mpData[Constants.ResultKey] : null;
			const pts = chartToPoints(chartObj);
			// TNP 透传(过滤交给 buildRings 统一裁剪,避免开关时还需重发请求)。
			if (mp && Array.isArray(mp.tnp)) mp.tnp.forEach((t) => pts.push({ id: t.id, lon: t.lon }));
			if (!this.unmounted) this.setState({ transitPoints: pts });
		} catch (e) { /* 静默 */ }
	}

	natalPoints(){
		const pts = chartToPoints(this.props.chart);
		// 全量入 + filterByTnp 在出口处裁剪,这样 TNP 开关切换无需重发后端请求,即时反映。
		(this.state.natalTnp || []).forEach((t) => pts.push({ id: t.id, lon: t.lon }));
		pts.push({ id: AstroConst.ARIES_POINT, lon: 0 }); // 白羊点/世界轴 = 0°（=AR 对称图）
		return filterByTnp(pts, this.state.showTnp);
	}

	// 真太阳弧：SA = λ_Sun(出生 + age 年) − λ_Sun(出生)，1 历日 = 1 年（spec §7.1，推荐默认）。
	async requestSolarArc(){
		const base = fieldsToParams(this.props.fields);
		const natalSun = sunLon(this.props.chart);
		const birth = this.props.fields && this.props.fields.date ? this.props.fields.date.value : null;
		const ms = birthEpochMs(birth);
		if (dialParamsError(base) || natalSun == null || !Number.isFinite(ms)) return;
		const ageYears = (Date.now() - ms) / (86400000 * 365.2422);
		const d = new Date(ms + ageYears * 86400000); // 出生 + age 日（1日=1年二次推进）
		const overrideLat = this.state.saLat, overrideLon = this.state.saLon;
		const loc = (overrideLat != null && overrideLon != null) ? { lat: overrideLat, lon: overrideLon, gpsLat: overrideLat, gpsLon: overrideLon } : {};
		const params = { ...base, ...loc, date: `${d.getFullYear()}/${pad(d.getMonth() + 1)}/${pad(d.getDate())}`, time: `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}` };
		try {
			const chartData = await request(`${Constants.ServerRoot}/chart`, { body: JSON.stringify({ ...params, cid: null }), silent: true });
			const co = chartData && chartData[Constants.ResultKey] ? chartData[Constants.ResultKey] : null;
			const progSun = sunLon(co);
			if (progSun != null && !this.unmounted) this.setState({ saArcDeg: (((progSun - natalSun) % 360) + 360) % 360 });
		} catch (e) { /* 退回近似 */ }
	}

	solarArcDeg(){
		if (this.state.saArcDeg != null) return this.state.saArcDeg; // 真太阳弧
		try {
			const birth = this.props.fields && this.props.fields.date ? this.props.fields.date.value : null;
			const ms = birthEpochMs(birth);
			if (!Number.isFinite(ms)) return 0;
			const days = (Date.now() - ms) / 86400000;
			return Math.max(0, days / 365.2422 * 0.9856473); // 退回 Naibod 近似
		} catch (e) { return 0; }
	}

	buildRings(){
		const natalPts = this.natalPoints();
		const rings = [{ key: 'natal', label: '本命', points: natalPts }];
		if (this.state.showTransit && this.state.transitPoints) {
			rings.push({ key: 'transit', label: '行运', points: filterByTnp(this.state.transitPoints, this.state.showTnp) });
		}
		// 太阳弧=交互式向运盘：初始贴本命(不预移)，拖动该环=向运,环旋转量即定向弧→反推年龄(见 onSaArc)。
		if (this.state.showSolarArc) {
			rings.push({ key: 'solararc', label: '太阳弧', points: natalPts });
		}
		return rings;
	}

	onReadout(readout){ this.setState({ readout }); }
	// 太阳弧环被拖动 → 报告定向弧(黄道度)；按 SA key 反推对应年龄。
	onSaArc(arc){
		const a = ((Number(arc) % 360) + 360) % 360;
		const rate = this.state.saKey === 'oneDeg' ? 1.0 : 0.9856473354; // 1°/年 或 Naibod
		this.setState({ saArcDirected: a, saAge: a / rate });
	}

	saveDisp(patch){ this.setState(patch); saveUranianDisplay(patch); }
	toggleTransit(v){ this.saveDisp({ showTransit: v }); if (v) this.requestTransit(); }

	buildTreeData(tree){
		return Object.keys(tree).map((pid) => ({
			title: (<span><b>{glyphOf(pid)}</b> <span style={{ color: 'var(--horosa-text-soft)', fontSize: 11 }}>· {tree[pid].length} 组</span></span>),
			key: pid,
			children: tree[pid].map((r, i) => ({
				title: (<span>{glyphOf(r.a)} <span style={{ color: 'var(--horosa-text-soft)' }}>/</span> {glyphOf(r.b)} <span style={{ color: 'var(--horosa-text-soft)', fontSize: 11 }}>- {r.sep.toFixed(2)}°</span></span>),
				key: pid + '_' + i, isLeaf: true,
			})),
		}));
	}

	// 三层叠盘信息（本命/行运/太阳弧）——让用户清楚每环是什么、对应何时。
	// 验收口径(2026-06-02):太阳弧 info 文案精简到只剩用户关心的弧度+年龄,避免左栏被截断。
	layerRows(){
		const f = this.props.fields || {};
		const fmtF = (k, p) => { const v = f[k] && f[k].value; return (v && v.format) ? v.format(p) : '—'; };
		const birthText = `${fmtF('date', 'YYYY-MM-DD')} ${fmtF('time', 'HH:mm')}`.trim();
		const now = new Date();
		const nowText = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;
		const transitText = this.state.transitTime ? this.state.transitTime.format('YYYY-MM-DD HH:mm') : `此刻 ${nowText}`;
		const saArc = this.state.saArcDirected || 0;
		const saAge = this.state.saAge || 0;
		const saKeyLabel = this.state.saKey === 'oneDeg' ? '1°/年' : 'Naibod';
		return [
			{ key: 'natal', label: '本命', dot: '#5b6470', info: `出生 ${birthText}`, locked: true, on: true },
			{ key: 'transit', label: '行运', dot: '#c0392b', info: transitText, on: this.state.showTransit, toggle: (v) => this.toggleTransit(v) },
			{ key: 'solararc', label: '太阳弧', dot: '#1f7a5a', info: `弧 ${saArc.toFixed(1)}° → 约 ${saAge.toFixed(1)} 岁（${saKeyLabel}）`, on: this.state.showSolarArc, toggle: (v) => this.toggleSolarArc(v) },
		];
	}

	renderDial(size, rings){
		const common = {
			rings, base: this.state.dialBase, orb: this.state.orb,
			showTnp: this.state.showTnp, size, onCursorChange: this.onReadout, onSaArc: this.onSaArc,
			personal: PERSONAL_POINTS, onlyPersonal: this.state.onlyPersonal,
		};
		return this.state.dialStyle === 'modulus'
			? <UranianModulusDial {...common} />
			: <UranianDial {...common} />;
	}

	// 行运/SA 地点输入框（占位=本命的 lat/lon）。空=用本命；填数=覆盖。
	renderLocOverride(latKey, lonKey, onCommit){
		const natalLat = fv(this.props.fields, 'lat');
		const natalLon = fv(this.props.fields, 'lon');
		const set = (k) => (v) => { this.setState({ [k]: parseNum(v) }, () => { if (onCommit) onCommit(); }); };
		const cell = { display: 'inline-block', width: 'calc(50% - 4px)' };
		const headStyle = { fontSize: 11, color: 'var(--horosa-text-soft)', marginBottom: 3 };
		return (
			<div>
				<div style={headStyle}>地点（空=同本命）</div>
				<div style={{ display: 'flex', gap: 8 }}>
					<div style={cell}>
						<InputNumber size="small" placeholder={natalLat != null ? `${natalLat}` : '纬度'} value={this.state[latKey]}
							onChange={set(latKey)} step={0.001} style={{ width: '100%' }} controls={false} />
					</div>
					<div style={cell}>
						<InputNumber size="small" placeholder={natalLon != null ? `${natalLon}` : '经度'} value={this.state[lonKey]}
							onChange={set(lonKey)} step={0.001} style={{ width: '100%' }} controls={false} />
					</div>
				</div>
			</div>
		);
	}

	render(){
		const height = this.props.height ? this.props.height : 760;
		const rings = this.buildRings();
		const natalPts = rings[0].points;
		const size = Math.max(480, Math.min(height - 2, 1000));
		// 中点树仅本命点(同 §11);TNP 过滤已在 natalPoints() 入口完成。
		const treeOpts = { personal: PERSONAL_POINTS, onlyPersonal: this.state.onlyPersonal };
		const tree = this.state.showPicture ? midpointTree(natalPts, this.state.dialBase, this.state.orb, treeOpts) : {};
		const ringTone = { 本命: 'var(--horosa-text-strong, currentColor)', 行运: '#c0392b', 太阳弧: '#1f7a5a' };
		const cardProps = { size: 'small', bordered: true, className: 'horosa-uranian-card', headStyle: { fontSize: 13, fontWeight: 600, minHeight: 34, padding: '0 12px' }, bodyStyle: { padding: '10px 12px' }, style: { marginBottom: 10 } };
		const rowSty = { display: 'flex', justifyContent: 'space-between', alignItems: 'center' };
		const layers = this.layerRows();

		const settings = (
			<div style={{ width: '100%' }}>
				<Card {...cardProps} title="盘式与盘基">
					<Radio.Group size="small" value={this.state.dialStyle} onChange={(e) => this.saveDisp({ dialStyle: e.target.value })} style={{ width: '100%', marginBottom: 10 }}>
						<Radio.Button value="folded" style={{ width: '50%', textAlign: 'center' }}>折叠盘</Radio.Button>
						<Radio.Button value="modulus" style={{ width: '50%', textAlign: 'center' }}>多环模数盘</Radio.Button>
					</Radio.Group>
					<div style={{ color: 'var(--horosa-text-soft)', fontSize: 12, marginBottom: 4 }}>盘基（模数）</div>
					<Select value={this.state.dialBase} onChange={(v) => this.saveDisp({ dialBase: Number(v) })} style={{ width: '100%' }} size="small">
						{URANIAN_DIAL_BASES.map((b) => <Option key={b} value={b}>{dialBaseLabel(b)} 盘</Option>)}
					</Select>
				</Card>

				<Card {...cardProps} title="叠盘层（除本命外可拖动）">
					{layers.map((L) => (
						<div key={L.key} style={{ ...rowSty, padding: '5px 0', borderBottom: L.key !== 'solararc' ? '1px solid var(--horosa-border-soft, rgba(0,0,0,0.04))' : 'none' }}>
							<div style={{ minWidth: 0, flex: 1 }}>
								<div><span style={{ color: L.dot, marginRight: 5 }}>●</span><b>{L.label}</b>{L.locked ? <span style={{ color: 'var(--horosa-text-soft)', fontSize: 11 }}> · 锁定</span> : null}</div>
								{/* 不截断:换行而非省略号(用户验收口径)。 */}
								<div style={{ color: 'var(--horosa-text-soft)', fontSize: 11, marginLeft: 16, wordBreak: 'break-word', whiteSpace: 'normal' }}>{L.info}</div>
							</div>
							{L.locked ? <span style={{ color: 'var(--horosa-text-soft)', fontSize: 11 }}>内圈</span> : <Switch size="small" checked={L.on} onChange={L.toggle} />}
						</div>
					))}
					{this.state.showTransit ? (
						<div style={{ marginTop: 8 }}>
							<div style={{ fontSize: 11, color: 'var(--horosa-text-soft)', marginBottom: 3 }}>行运时刻</div>
							<DatePicker size="small" showTime format="YYYY-MM-DD HH:mm" value={this.state.transitTime}
								placeholder="此刻" style={{ width: '100%' }}
								onChange={(v) => this.setState({ transitTime: v }, () => this.requestTransit())} />
							<div style={{ marginTop: 6 }}>{this.renderLocOverride('transitLat', 'transitLon', () => this.requestTransit())}</div>
						</div>
					) : null}
					{this.state.showSolarArc ? (
						<div style={{ marginTop: 10 }}>
							<div style={rowSty}>
								<span style={{ fontSize: 11, color: 'var(--horosa-text-soft)' }}>太阳弧换算</span>
								<Radio.Group size="small" value={this.state.saKey} onChange={(e) => { const k = e.target.value; this.saveDisp({ saKey: k }); const rate = k === 'oneDeg' ? 1.0 : 0.9856473354; this.setState({ saAge: (this.state.saArcDirected || 0) / rate }); }}>
									<Radio.Button value="naibod">Naibod</Radio.Button>
									<Radio.Button value="oneDeg">1°/年</Radio.Button>
								</Radio.Group>
							</div>
							<div style={{ marginTop: 6 }}>{this.renderLocOverride('saLat', 'saLon')}</div>
						</div>
					) : null}
				</Card>

				<Card {...cardProps} title="显示与读数">
					<div style={{ ...rowSty, marginBottom: 8 }}><span>TNP 虚星</span><Switch size="small" checked={this.state.showTnp} onChange={(v) => this.saveDisp({ showTnp: v })} /></div>
					<div style={{ ...rowSty, marginBottom: 8 }}><span>中点树扫描</span><Switch size="small" checked={this.state.showPicture} onChange={(v) => this.saveDisp({ showPicture: v })} /></div>
					<div style={{ ...rowSty, marginBottom: 10 }}><span>仅含个人点</span><Switch size="small" checked={this.state.onlyPersonal} onChange={(v) => this.saveDisp({ onlyPersonal: v })} /></div>
					<div style={{ marginBottom: 2, fontSize: 12 }}>容许度 <b>{this.state.orb}°</b></div>
					<Slider min={0.5} max={3} step={0.5} value={this.state.orb} onChange={(v) => this.saveDisp({ orb: v })} />
				</Card>
			</div>
		);

		// 指针读数:用短横线 '-' 标距(原希腊符像三角不友好);单行 nowrap 防换行;TNP 过滤已在源头完成(natalPoints/transit),此处直接信任。
		const readoutBody = this.state.readout.length === 0
			? <div style={{ color: 'var(--horosa-text-soft)', fontSize: 12 }}>拖动行运/太阳弧环或红指针，对齐处的星体/中点会列在这里。</div>
			: this.state.readout.slice(0, 60).map((h, i) => (
				<div key={i} style={{ lineHeight: 2.0, fontSize: 13, whiteSpace: 'nowrap' }}>
					{rings.length > 1 ? <span style={{ color: ringTone[h.ring] || 'var(--horosa-text-soft)', fontSize: 11, fontWeight: 600 }}>[{h.ring}] </span> : null}
					{h.kind === 'body'
						? <span>轴 = <b>{glyphOf(h.id)}</b> <span style={{ color: 'var(--horosa-text-soft)' }}>- {h.sep.toFixed(2)}°</span></span>
						: <span>轴 = {glyphOf(h.a)}<span style={{ color: 'var(--horosa-text-soft)' }}>/</span>{glyphOf(h.b)} <span style={{ color: 'var(--horosa-text-soft)' }}>- {h.sep.toFixed(2)}°</span></span>}
				</div>
			));

		const treeData = this.buildTreeData(tree);
		const treeBody = treeData.length === 0
			? <div style={{ color: 'var(--horosa-text-soft)', fontSize: 12 }}>容许度内暂无中点结构</div>
			: <Tree treeData={treeData} showLine={{ showLeafIcon: false }} blockNode selectable={false} defaultExpandedKeys={treeData.slice(0, 3).map((n) => n.key)} />;

		const rightCol = (
			<div style={{ width: '100%' }}>
				<Card {...cardProps} title="指针读数" bodyStyle={{ padding: '8px 12px', maxHeight: Math.round(size * 0.52), overflowY: 'auto', overflowX: 'auto' }}>{readoutBody}</Card>
				<Card {...cardProps} title="中点树" bodyStyle={{ padding: '8px 12px', maxHeight: Math.round(size * 0.4), overflowY: 'auto', overflowX: 'auto' }}>{treeBody}</Card>
			</div>
		);

		// 列宽:左 4 / 中 16 / 右 4 = 24(从 4/17/3 调整;右栏 +1 防换行,中栏只 -1 仍占主体)。
		return (
			<div className="horosa-midpoint-host">
				<div className="horosa-midpoint-workbench">
					<Row className="horosa-midpoint-layout" gutter={10}>
						<Col span={4} className="horosa-midpoint-side-col">{settings}</Col>
						<Col span={16} className="horosa-midpoint-chart-col">
							{natalPts.length === 0 ? (
								<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: size, color: 'var(--horosa-text-soft)', textAlign: 'center', padding: 24 }}>
									{this.state.dataNote || '请先排出本命盘后查看中点盘'}
								</div>
							) : (
								<div>
									{this.renderDial(size, rings)}
									{this.state.dataNote ? (
										<div style={{ textAlign: 'center', color: 'var(--horosa-text-soft)', fontSize: 12, marginTop: 6 }}>
											{this.state.dataNote}（TNP/行运/太阳弧 需完整出生信息）
										</div>
									) : null}
								</div>
							)}
						</Col>
						<Col span={4} className="horosa-midpoint-side-col">{rightCol}</Col>
					</Row>
				</div>
			</div>
		);
	}
}
