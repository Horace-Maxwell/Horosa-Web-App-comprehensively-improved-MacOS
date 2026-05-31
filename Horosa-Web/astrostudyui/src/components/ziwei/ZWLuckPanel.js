import { Component } from 'react';
import { Lunar, LunarMonth } from 'lunar-javascript';
import * as ZWConst from '../../constants/ZWConst';
import * as ZiWeiHelper from './ZiWeiHelper';
import DateTime from '../comp/DateTime';

const DIZI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const GANS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const LUNAR_MONTH = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月'];
const SHICHEN = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const HUA_BG = { '禄': '#c9912e', '权': '#2868d8', '科': '#1497a8', '忌': '#d44d43' };
const LEVEL_LABEL = { daxian: '大限', liunian: '流年', xiaoxian: '小限', liuyue: '流月', liuri: '流日', liushi: '流时' };

// ——— 干支基础（纯前端，绝不返回 undefined） ———
function yearGanzi(year) {
	if (!Number.isFinite(year)) return '';
	const gi = (((year - 4) % 10) + 10) % 10;
	const zi = (((year - 4) % 12) + 12) % 12;
	return GANS[gi] + DIZI[zi];
}
// 五虎遁：年干 → 正月天干顺推
function monthGan(yearGan, monthIdx /*0=正月*/) {
	const start = ZWConst.WuHuDun ? ZWConst.WuHuDun[yearGan] : null;
	const si = GANS.indexOf(start);
	if (si < 0) return '';
	return GANS[(si + monthIdx) % 10];
}
// 五鼠遁：日干 → 子时天干
const ZI_HOUR_START = { '甲': '甲', '己': '甲', '乙': '丙', '庚': '丙', '丙': '戊', '辛': '戊', '丁': '庚', '壬': '庚', '戊': '壬', '癸': '壬' };
function hourGan(dayGan, hourIdx /*0=子*/) {
	const si = GANS.indexOf(ZI_HOUR_START[dayGan]);
	if (si < 0) return '';
	return GANS[(si + hourIdx) % 10];
}
// 连续 JDN → 日干支（锚点 2026-05-18=壬辰[jiazi 28]，与 BaZiLuckFlowPanel 同源，绝对单调）
const DAY_ANCHOR_UNIX = Math.floor(Date.UTC(2026, 4, 18) / 86400000);
const DAY_ANCHOR_IDX = 28;
function dayGanziByDate(date) {
	const unix = Math.floor(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) / 86400000);
	const idx = (((unix - DAY_ANCHOR_UNIX + DAY_ANCHOR_IDX) % 60) + 60) % 60;
	return GANS[idx % 10] + DIZI[idx % 12];
}
// 小限起宫(虚岁一岁)：寅午戌→辰、申子辰→戌、亥卯未→丑、巳酉丑→未
const XIAOXIAN_START = {
	'寅': '辰', '午': '辰', '戌': '辰', '申': '戌', '子': '戌', '辰': '戌',
	'亥': '丑', '卯': '丑', '未': '丑', '巳': '未', '酉': '未', '丑': '未',
};

// houses[] 是连续地支但起始宫不固定 → 必须按地支搜数组下标，不可用 DIZI 位置
function houseIdxByBranch(chart, zhi) {
	if (!chart || !chart.houses || !zhi) return -1;
	return chart.houses.findIndex((h) => h && h.ganzi && h.ganzi.charAt(1) === zhi);
}
function houseName(chart, idx, short) {
	if (!chart || !chart.houses || idx === undefined || idx === null || idx < 0) return '—';
	const h = chart.houses[idx];
	const name = h && h.name ? h.name : '—';
	return short ? name.replace(/[宫宮]$/, '') : name;
}
function birthYearOf(chart) {
	if (chart && chart.birth) {
		const y = parseInt(`${chart.birth}`.substr(0, 4), 10);
		if (!Number.isNaN(y)) return y;
	}
	return 2000;
}

// ——— 各层 item 构造 ———
function buildDaxianItems(chart) {
	if (!chart || !chart.houses) return [];
	const arr = [];
	for (let i = 0; i < 12; i++) {
		const d = chart.houses[i] && chart.houses[i].direction;
		if (d) arr.push({ i, start: d[0], end: d[1], ganzi: chart.houses[i].ganzi });
	}
	arr.sort((a, b) => a.start - b.start);
	return arr.map((x) => ({
		id: `dx-${x.i}`, level: 'daxian', mingIndex: x.i, ganzi: x.ganzi,
		gan: x.ganzi.charAt(0), zhi: x.ganzi.charAt(1), start: x.start, end: x.end,
		top: `${x.start}~${x.end}`, sub: `${x.ganzi}限`,
	}));
}
// 流年：大限内 10 年（虚岁 n → 公历 birthYear+n-1）
function buildLiunianItems(chart, daxian) {
	if (!chart || !daxian) return [];
	const birthY = birthYearOf(chart);
	const startYear = birthY + daxian.start - 1;
	const out = [];
	for (let k = 0; k < (daxian.end - daxian.start + 1); k++) {
		const year = startYear + k;
		const gz = yearGanzi(year);
		if (!gz || gz.length < 2) continue;
		const zhi = gz.charAt(1);
		out.push({
			id: `ln-${year}`, level: 'liunian', year, age: daxian.start + k, ganzi: gz,
			gan: gz.charAt(0), zhi, mingIndex: houseIdxByBranch(chart, zhi),
			top: `${year}`, sub: `${gz}`,
		});
	}
	return out;
}
// 小限：与流年同级——大限内 10 个虚岁（男顺女逆、不分阴阳；干支复用本命宫位）
function buildXiaoxianItems(chart, daxian) {
	if (!chart || !chart.houses || !chart.yearZi || !daxian) return [];
	const startZhi = XIAOXIAN_START[chart.yearZi];
	if (!startZhi) return [];
	const startIdx = houseIdxByBranch(chart, startZhi);
	if (startIdx < 0) return [];
	const male = chart.gender === 'Male' || chart.gender === 1 || chart.gender === '1';
	const birthY = birthYearOf(chart);
	const out = [];
	for (let age = daxian.start; age <= daxian.end; age++) {
		const step = age - 1;
		const idx = male ? (startIdx + step) % 12 : ((startIdx - step) % 12 + 12) % 12;
		const house = chart.houses[idx];
		if (!house) continue;
		const ganzi = house.ganzi;
		out.push({
			id: `xx-${age}`, level: 'xiaoxian', age, year: birthY + age - 1, mingIndex: idx,
			ganzi, gan: ganzi.charAt(0), zhi: ganzi.charAt(1),
			top: `${age}岁`, sub: `${ganzi}`,
		});
	}
	return out;
}
// 流月：由当前年(流年或小限所在年)展开。斗君宫=getDouJun(子斗,年支)；正月起斗君宫顺行
function buildLiuyueItems(chart, year) {
	if (!chart || !Number.isFinite(year)) return [];
	const gz = yearGanzi(year);
	const yearGan = gz.charAt(0);
	const yearZhi = gz.charAt(1);
	const doujunZhi = ZiWeiHelper.getDouJun(chart.zidou, yearZhi);
	const doujunIdx = houseIdxByBranch(chart, doujunZhi);
	const out = [];
	for (let m = 0; m < 12; m++) {
		const gan = monthGan(yearGan, m);
		const zhi = DIZI[(2 + m) % 12]; // 正月建寅
		const mingIndex = doujunIdx < 0 ? -1 : (doujunIdx + m) % 12;
		out.push({
			id: `ly-${year}-${m}`, level: 'liuyue', month: m + 1, year,
			ganzi: gan + zhi, gan, zhi, mingIndex,
			top: LUNAR_MONTH[m], sub: `${gan}${zhi}`,
		});
	}
	return out;
}
// 流日：流月命宫 + (日-1)；日干支连续 JDN
function buildLiuriItems(chart, year, liuyue) {
	if (!chart || !liuyue) return [];
	let days = 30;
	let firstSolar = null;
	try {
		const lm = LunarMonth.fromYm(year, liuyue.month);
		if (lm && typeof lm.getDayCount === 'function') days = lm.getDayCount();
	} catch (e) { days = 30; }
	try {
		const s = Lunar.fromYmd(year, liuyue.month, 1).getSolar();
		firstSolar = new Date(s.getYear(), s.getMonth() - 1, s.getDay());
	} catch (e) { firstSolar = null; }
	const out = [];
	for (let d = 1; d <= days; d++) {
		let ganzi = '';
		if (firstSolar) {
			const dt = new Date(firstSolar.getFullYear(), firstSolar.getMonth(), firstSolar.getDate() + (d - 1));
			ganzi = dayGanziByDate(dt);
		}
		const zhi = ganzi ? ganzi.charAt(1) : '';
		const mingIndex = (liuyue.mingIndex + (d - 1)) % 12;
		out.push({
			id: `lr-${year}-${liuyue.month}-${d}`, level: 'liuri', day: d, year,
			ganzi, gan: ganzi ? ganzi.charAt(0) : '', zhi, mingIndex,
			top: `${d}`, sub: ganzi || `${d}日`,
		});
	}
	return out;
}
// 流时：流日命宫 + 时辰序；五鼠遁日干→时干
function buildLiushiItems(chart, liuri) {
	if (!chart || !liuri || !liuri.gan) return [];
	const out = [];
	for (let h = 0; h < 12; h++) {
		const gan = hourGan(liuri.gan, h);
		const zhi = DIZI[h];
		const mingIndex = (liuri.mingIndex + h) % 12;
		out.push({
			id: `ls-${liuri.day}-${h}`, level: 'liushi', hourIdx: h,
			ganzi: gan + zhi, gan, zhi, mingIndex,
			top: `${SHICHEN[h]}时`, sub: `${gan}${zhi}`,
		});
	}
	return out;
}

class ZWLuckPanel extends Component {
	constructor(props) {
		super(props);
		this.state = this.initState(props);
	}

	initState(props) {
		const chart = props.chart || {};
		let nowYear = 2000;
		try { nowYear = parseInt(new DateTime().format('YYYY'), 10); } catch (e) { /* noop */ }
		const daxianItems = buildDaxianItems(chart);
		let dx = daxianItems[0] || null;
		if (chart.birth && daxianItems.length) {
			const age = nowYear - birthYearOf(chart) + 1;
			dx = daxianItems.find((d) => d.start <= age && age <= d.end) || daxianItems[0];
		}
		const liunianItems = dx ? buildLiunianItems(chart, dx) : [];
		const ln = liunianItems.find((y) => y.year === nowYear) || liunianItems[0] || null;
		return {
			annualMode: 'liunian',
			daxian: dx, liunian: ln, xiaoxian: null,
			liuyue: null, liuri: null, liushi: null,
		};
	}

	componentDidMount() { this.emit(); }
	componentDidUpdate(prev) {
		if (prev.chart !== this.props.chart) {
			this.setState(this.initState(this.props), this.emit);
		}
	}

	// 当前激活的「年级」层（流年 or 小限）
	activeAnnual() {
		return this.state.annualMode === 'liunian' ? this.state.liunian : this.state.xiaoxian;
	}
	activeYear() {
		const a = this.activeAnnual();
		return a && Number.isFinite(a.year) ? a.year : null;
	}
	// 最深选中层（驱动盘面流命环）
	deepest() {
		const s = this.state;
		return s.liushi || s.liuri || s.liuyue || this.activeAnnual() || s.daxian || null;
	}
	emit() {
		if (!this.props.onLuckChange) return;
		const d = this.deepest();
		this.props.onLuckChange(d ? d.mingIndex : null);
	}

	pickDaxian(item) {
		const chart = this.props.chart || {};
		const ln = buildLiunianItems(chart, item)[0] || null;
		const xx = buildXiaoxianItems(chart, item)[0] || null;
		this.setState({ daxian: item, liunian: ln, xiaoxian: xx, liuyue: null, liuri: null, liushi: null }, this.emit);
	}
	setAnnualMode(mode) {
		const chart = this.props.chart || {};
		// 切换年级模式时，确保该模式有默认选中，并清空下层
		const patch = { annualMode: mode, liuyue: null, liuri: null, liushi: null };
		if (mode === 'liunian' && !this.state.liunian && this.state.daxian) {
			patch.liunian = buildLiunianItems(chart, this.state.daxian)[0] || null;
		}
		if (mode === 'xiaoxian' && !this.state.xiaoxian && this.state.daxian) {
			patch.xiaoxian = buildXiaoxianItems(chart, this.state.daxian)[0] || null;
		}
		this.setState(patch, this.emit);
	}
	pickLiunian(item) { this.setState({ annualMode: 'liunian', liunian: item, liuyue: null, liuri: null, liushi: null }, this.emit); }
	pickXiaoxian(item) { this.setState({ annualMode: 'xiaoxian', xiaoxian: item, liuyue: null, liuri: null, liushi: null }, this.emit); }
	pickLiuyue(item) { this.setState({ liuyue: item, liuri: null, liushi: null }, this.emit); }
	pickLiuri(item) { this.setState({ liuri: item, liushi: null }, this.emit); }
	pickLiushi(item) { this.setState({ liushi: item }, this.emit); }

	renderAxis(label, items, selectedId, onClick, key) {
		if (!items || !items.length) return null;
		return (
			<div className="horosa-ziwei-luck-axis-row" key={key || label}>
				<div className="horosa-ziwei-luck-axis-label">{label}</div>
				<div className="horosa-ziwei-luck-axis">
					{items.map((item) => (
						<button type="button" key={item.id}
							className={`horosa-ziwei-luck-chip ${item.id === selectedId ? 'is-selected' : ''}`}
							onClick={() => onClick(item)}>
							<span className="chip-top">{item.top}</span>
							<span className="chip-sub">{item.sub}</span>
						</button>
					))}
				</div>
			</div>
		);
	}

	// 年级行：左侧为 流年/小限 互斥 toggle，右侧为当前模式的 chips
	renderAnnualRow(liunianItems, xiaoxianItems) {
		const { annualMode, liunian, xiaoxian } = this.state;
		const items = annualMode === 'liunian' ? liunianItems : xiaoxianItems;
		const selId = annualMode === 'liunian' ? (liunian && liunian.id) : (xiaoxian && xiaoxian.id);
		const onClick = annualMode === 'liunian' ? (i) => this.pickLiunian(i) : (i) => this.pickXiaoxian(i);
		return (
			<div className="horosa-ziwei-luck-axis-row">
				<div className="horosa-ziwei-luck-axis-toggle">
					<button type="button" className={annualMode === 'liunian' ? 'on' : ''} onClick={() => this.setAnnualMode('liunian')}>流年</button>
					<button type="button" className={annualMode === 'xiaoxian' ? 'on' : ''} onClick={() => this.setAnnualMode('xiaoxian')}>小限</button>
				</div>
				<div className="horosa-ziwei-luck-axis">
					{(items || []).map((item) => (
						<button type="button" key={item.id}
							className={`horosa-ziwei-luck-chip ${item.id === selId ? 'is-selected' : ''}`}
							onClick={() => onClick(item)}>
							<span className="chip-top">{item.top}</span>
							<span className="chip-sub">{item.sub}</span>
						</button>
					))}
				</div>
			</div>
		);
	}

	// 单层四化卡
	renderLayerCard(layer) {
		if (!layer) return null;
		const chart = this.props.chart || {};
		const mingIdx = layer.mingIndex;
		const oppIdx = (mingIdx + 6) % 12;
		const sihua = ZiWeiHelper.getLayerSihua(chart, layer.gan) || [];
		const flowStars = (layer.level === 'liunian') ? (ZiWeiHelper.getFlowStars(layer.gan, layer.zhi) || []) : [];
		let sub = '';
		if (layer.level === 'liunian' && layer.year) sub = `${layer.year}年`;
		else if (layer.level === 'xiaoxian' && layer.age) sub = `${layer.age}虚岁`;
		else if (layer.level === 'liuyue' && layer.month) sub = LUNAR_MONTH[layer.month - 1] || '';
		else if (layer.level === 'liuri' && layer.day) sub = `${layer.day}日`;
		else if (layer.level === 'daxian') sub = `${layer.start}~${layer.end}岁`;
		return (
			<div className={`horosa-ziwei-luck-card cat-${layer.level}`} key={layer.id}>
				<div className="horosa-ziwei-luck-card-head">
					<span className="horosa-ziwei-luck-badge">{LEVEL_LABEL[layer.level]}</span>
					<span className="horosa-ziwei-luck-ganzi">{layer.ganzi}</span>
					{sub && <span className="horosa-ziwei-luck-sub-tag">{sub}</span>}
					<span className="horosa-ziwei-luck-pal-inline">命【{houseName(chart, mingIdx, true)}】·对【{houseName(chart, oppIdx, true)}】</span>
				</div>
				<div className="horosa-ziwei-luck-sihua">
					{sihua.map((h) => (
						<span key={h.star} className="hua" style={{ background: HUA_BG[h.hua] || '#888' }}>
							<b>{h.hua}</b>{h.star}<i>{houseName(chart, h.houseIndex, true)}</i>
						</span>
					))}
				</div>
				{flowStars.length > 0 && (
					<div className="horosa-ziwei-luck-flow">
						{flowStars.map((s) => (
							<span key={s.name} className="flow-chip">{s.name}<i>{houseName(chart, houseIdxByBranch(chart, s.zhi), true)}</i></span>
						))}
					</div>
				)}
			</div>
		);
	}

	render() {
		const chart = this.props.chart || {};
		const s = this.state;
		if (!chart || !chart.houses) {
			return <div className="horosa-empty-hint">起盘后查看运限</div>;
		}
		const daxianItems = buildDaxianItems(chart);
		const liunianItems = s.daxian ? buildLiunianItems(chart, s.daxian) : [];
		const xiaoxianItems = s.daxian ? buildXiaoxianItems(chart, s.daxian) : [];
		const year = this.activeYear();
		const liuyueItems = year ? buildLiuyueItems(chart, year) : [];
		const liuriItems = (year && s.liuyue) ? buildLiuriItems(chart, year, s.liuyue) : [];
		const liushiItems = s.liuri ? buildLiushiItems(chart, s.liuri) : [];

		// 卡片栈：每个已选层级各一张（大限 + 年级 + 流月? + 流日? + 流时?）
		const cards = [];
		if (s.daxian) cards.push(s.daxian);
		const annual = this.activeAnnual();
		if (annual) cards.push(annual);
		if (s.liuyue) cards.push(s.liuyue);
		if (s.liuri) cards.push(s.liuri);
		if (s.liushi) cards.push(s.liushi);

		return (
			<div className="horosa-ziwei-luck">
				<div className="horosa-ziwei-luck-axes">
					{this.renderAxis('大限', daxianItems, s.daxian ? s.daxian.id : '', (i) => this.pickDaxian(i), 'dx')}
					{this.renderAnnualRow(liunianItems, xiaoxianItems)}
					{liuyueItems.length > 0 && this.renderAxis('流月', liuyueItems, s.liuyue ? s.liuyue.id : '', (i) => this.pickLiuyue(i), 'ly')}
					{liuriItems.length > 0 && this.renderAxis('流日', liuriItems, s.liuri ? s.liuri.id : '', (i) => this.pickLiuri(i), 'lr')}
					{liushiItems.length > 0 && this.renderAxis('流时', liushiItems, s.liushi ? s.liushi.id : '', (i) => this.pickLiushi(i), 'ls')}
				</div>
				<div className="horosa-ziwei-luck-cards">
					{cards.map((c) => this.renderLayerCard(c))}
				</div>
				<div className="horosa-ziwei-luck-note">
					<span>断同大限，尤重对宫与三合</span>
					{this.props.onAi && <a onClick={this.props.onAi}>AI解读 ›</a>}
				</div>
			</div>
		);
	}
}

export default ZWLuckPanel;
