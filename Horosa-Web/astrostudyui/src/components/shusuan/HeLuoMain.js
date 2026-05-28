import { Component } from 'react';
import { Empty } from 'antd';
import { Solar } from 'lunar-javascript';
import { XQTabs as Tabs } from '../xq-ui';
import { buildLocalBaziResult } from '../../utils/baziLunarLocal';
import { defaultAfter23NewDay, defaultLateZiHourUseNextDay } from '../../utils/dayBoundary';
import calc, {
	daYun, liuNian, liuYue, liuRi, judge, periodLiShu, guaRelations, chartExtras, duiGua, solarTermHuagong,
	yaoText, guaInfo, yaoName, buildSnapshotText, NAME_TO_TRI, guaLines,
} from '../../utils/heluoLocal';
import { Gua64 } from '../gua/GuaConst';   // 复用 六爻/统摄法 的纳甲六亲世应
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';

// 纳甲天干（内卦/外卦）：仅乾坤内外异，余卦内外同
const NAJIA_GAN = { 乾: ['甲', '壬'], 坤: ['乙', '癸'], 震: ['庚', '庚'], 巽: ['辛', '辛'], 坎: ['戊', '戊'], 離: ['己', '己'], 艮: ['丙', '丙'], 兌: ['丁', '丁'] };
const LIUQIN_SHORT = { 父母: '父', 兄弟: '兄', 官鬼: '官', 妻财: '財', 妻財: '財', 子孙: '子', 子孫: '子' };
const { TabPane } = Tabs;

function fieldVal(fields, key, fallback = '') {
	if (!fields || !fields[key] || fields[key].value === undefined || fields[key].value === null) return fallback;
	return fields[key].value;
}

const LI_TERMS = ['立春', '立夏', '立秋', '立冬'];

// slot: 'center'(主信息·滑动) | 'aux'(辅助信息·卡片)。四柱来自 baziLunarLocal（星阙自己的八字，不走后端）。
class HeLuoMain extends Component {
	constructor(props) {
		super(props);
		this.state = { daxianKey: '', openYao: '', liunianKey: '', liuyueKey: '', yearForMonth: null, monthForDay: null };
		this.lastSnapKey = '';
	}

	componentDidMount() {
		this.saveSnap();
		// v2.2.1: 监听全局日界 / 晚子时·时柱起干切换 → 强制重渲(getModel 内部用 defaultAfter23NewDay/defaultLateZiHourUseNextDay 实时读 localStorage)。
		if(typeof window !== 'undefined'){
			this._dayBoundaryListener = () => { if(!this._unmounted) this.forceUpdate(); };
			this._lateZiHourListener = () => { if(!this._unmounted) this.forceUpdate(); };
			window.addEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
			window.addEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
		}
	}
	componentDidUpdate() { this.saveSnap(); }
	componentWillUnmount() {
		this._unmounted = true;
		if(typeof window !== 'undefined'){
			if(this._dayBoundaryListener){
				window.removeEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
			}
			if(this._lateZiHourListener){
				window.removeEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
			}
		}
	}

	// 真实节气：化工(象限+土用) + 三候(节气内 5 日一候)。
	solarTerm(dateStr) {
		try {
			const [y, m, d] = dateStr.split('-').map((x) => parseInt(x, 10));
			const solar = Solar.fromYmd(y, m, d);
			const lunar = solar.getLunar();
			const prev = lunar.getPrevJieQi(true);
			const prevName = prev.getName();
			const jd = solar.getJulianDay();
			const tbl = lunar.getJieQiTable();
			const tuyong = LI_TERMS.some((n) => {
				const t = tbl[n];
				if (!t) return false;
				const diff = t.getJulianDay() - jd;
				return diff >= 0 && diff <= 18;
			});
			const daysIn = Math.max(0, Math.floor(jd - prev.getSolar().getJulianDay()));
			const hou = Math.min(3, Math.floor(daysIn / 5) + 1);
			const houLabel = `${prevName}${['初候', '二候', '三候'][hou - 1]}·${prevName}後`;
			return { ...solarTermHuagong(prevName, tuyong), term: prevName, hou, houLabel };
		} catch (e) { return null; }
	}

	getModel() {
		const f = this.props.fields || {};
		const dateMoment = f.date && f.date.value ? f.date.value : null;
		const timeMoment = f.time && f.time.value ? f.time.value : null;
		if (!dateMoment || !timeMoment) return null;
		const dateStr = dateMoment.format('YYYY-MM-DD');
		const params = {
			date: dateStr,
			time: timeMoment.format('HH:mm:ss'),
			lon: fieldVal(f, 'lon', ''),
			gender: fieldVal(f, 'gender', 1),
			timeAlg: fieldVal(f, 'timeAlg', 1),
			after23NewDay: defaultAfter23NewDay(),
			lateZiHourUseNextDay: defaultLateZiHourUseNextDay(),
		};
		let bazi;
		try { bazi = buildLocalBaziResult(params).bazi; } catch (e) { return null; }
		const fc = (bazi && bazi.fourColumns) || {};
		const gz = (p) => (p && (p.ganzi || p.ganZhi)) || '';
		const fourPillars = { year: gz(fc.year), month: gz(fc.month), day: gz(fc.day), hour: gz(fc.time) };
		if (!fourPillars.year || !fourPillars.month || !fourPillars.day || !fourPillars.hour) return null;
		const monthZhi = fourPillars.month.charAt(1);
		const hourZhi = fourPillars.hour.charAt(1);
		const birthYear = parseInt(dateStr.slice(0, 4), 10) || 0;
		const gender = bazi.gender === 'Female' ? '女' : '男';
		let chart;
		try { chart = calc({ fourPillars, gender, hourZhi, birthYear, monthZhi }); } catch (e) { return null; }
		if (!chart.xian.name || !chart.hou.name) return null;
		const dy = daYun(chart.xian, chart.hou, birthYear);
		const st = this.solarTerm(dateStr);
		const jg = judge(chart, fourPillars, monthZhi, st);
		const nayinStr = (fc.year && (fc.year.naying || fc.year.nayin)) || '';
		const nayin = '金木水火土'.includes(nayinStr.slice(-1)) ? nayinStr.slice(-1) : '';
		const extras = chartExtras(chart, fourPillars, monthZhi, jg, { sanhou: st ? st.houLabel : '', nayin });
		return { fourPillars, monthZhi, hourZhi, birthYear, gender, chart, dy, jg, st, nayin: nayinStr, extras };
	}

	saveSnap() {
		if (this.props.slot === 'aux') return;
		const m = this.getModel();
		if (!m) return;
		const key = `${m.chart.xian.name}|${m.chart.xian.yuan}|${m.chart.hou.name}`;
		if (key === this.lastSnapKey) return;
		this.lastSnapKey = key;
		const text = buildSnapshotText(m.chart, m.jg, m.dy);
		if (text) saveModuleAISnapshot('heluo', text, { source: 'react', savedAt: Date.now() });
	}

	// 纳甲六亲世应（复用 Gua64，按六爻 value 匹配）+ 天干补全成完整干支
	najia(name) {
		const t = NAME_TO_TRI[name];
		if (!t) return [];
		const lines = guaLines(t.up, t.low);
		const g64 = Gua64.find((g) => Array.isArray(g.value) && g.value.length === 6 && g.value.every((b, i) => b === lines[i]));
		const out = [];
		for (let p = 1; p <= 6; p += 1) {
			const tri = p <= 3 ? t.low : t.up;
			const gan = (NAJIA_GAN[tri] || ['', ''])[p <= 3 ? 0 : 1];
			let zhi = '';
			let liuqin = '';
			let shiYing = '';
			if (g64 && g64.yaoname && g64.yaoname[p - 1]) {
				const yn = g64.yaoname[p - 1];
				zhi = yn[0];
				let rest = yn.slice(2);
				const tail = rest.slice(-1);
				if (tail === '世' || tail === '应' || tail === '應') { shiYing = tail === '應' ? '应' : tail; rest = rest.slice(0, -1); }
				liuqin = LIUQIN_SHORT[rest] || rest;
			}
			out.push({ yao: p, ganzhi: gan + zhi, liuqin, shiYing });
		}
		return out;
	}

	// 六爻卦象图（自上而下：爻6→爻1）+ 纳甲六亲，元堂高亮
	renderGua(gua, najia) {
		const rows = [];
		for (let p = 6; p >= 1; p -= 1) {
			const yang = gua.lines[p - 1] === 1;
			const nj = (najia || []).find((x) => x.yao === p) || {};
			rows.push(
				<div key={p} className={`horosa-heluo-yaorow${p === gua.yuan ? ' is-yuan' : ''}`}>
					<span className="horosa-heluo-najia">{nj.liuqin}{nj.ganzhi}{nj.shiYing ? <em className="horosa-heluo-shiying"> {nj.shiYing}</em> : ''}</span>
					<span className="horosa-heluo-bar-wrap">
						{yang ? <span className="horosa-heluo-bar yang" /> : <span className="horosa-heluo-bar yin"><i /><i /></span>}
					</span>
					<span className="horosa-heluo-yaolabel">{yaoName(gua.lines, p)}{p === gua.yuan ? ' ·元堂' : ''}</span>
				</div>,
			);
		}
		return <div className="horosa-heluo-gua">{rows}</div>;
	}


	renderGuaCard(title, gua, jg, najia, slot) {
		const info = guaInfo(gua.name) || {};
		const dui = duiGua(gua.name);
		return (
			<div className="horosa-huangji-info-card horosa-heluo-guacard">
				<div className="horosa-huangji-info-heading">{title}</div>
				<div className="horosa-heluo-guahead">
					{this.renderGua(gua, najia)}
					<div className="horosa-heluo-guameta">
						<div className="horosa-heluo-guaname">{gua.name}<span className="horosa-heluo-verdict">{info.verdict}</span></div>
						<div className="horosa-heluo-yuanyao">元堂 · {yaoName(gua.lines, gua.yuan)}</div>
						<div className="horosa-heluo-gist">{info.gist}</div>
						<div className="horosa-heluo-dui">互卦 {dui.hu} · 覆卦 {dui.fu}</div>
						<div className="horosa-heluo-tags">{this.renderLiShu(gua.lines, jg)}</div>
					</div>
				</div>
				{this.renderYaoci(gua.name, gua.yuan, gua.lines, slot)}
			</div>
		);
	}

	// 理数 chips：先标命卦对体关系(正對/反對/互)，再列 本卦含/互卦藏/覆卦覆 的 元气化工(正/反)
	liShuChips(lines, jg, chart) {
		const rels = chart ? guaRelations(lines, chart).filter((r) => r.indexOf('即') < 0) : [];
		const items = periodLiShu(lines, jg);
		if (!rels.length && !items.length) return <span className="horosa-heluo-tag-none">—</span>;
		return [
			...rels.map((r) => <span key={r} className="horosa-heluo-tag is-rel">{r}</span>),
			...items.map((it) => <span key={it.text} className={`horosa-heluo-tag${it.fan ? ' is-fan' : ''}`}>{it.text}</span>),
		];
	}

	renderLiShu(lines, jg, chart) { return this.liShuChips(lines, jg, chart); }

	liShuCell(lines, jg, chart) { return this.liShuChips(lines, jg, chart); }

	// 爻辞：命卦对体关系 + 摘要(河洛爻辞详解) + 诗歌(卦訣) + 倪海厦·易经推命(按 slot 取先天/后天/流年)
	renderYaoci(guaName2, pos, lines, slot, chart) {
		const info = guaInfo(guaName2) || {};
		const yt = yaoText(guaName2, pos) || {};
		const ni = (info.mingtiao || {})[slot || 'liunian'] || '';
		const rels = chart ? guaRelations(lines, chart).filter((r) => r.indexOf('即') < 0) : [];
		if (!yt.shige && !yt.detail && !ni) return <div className="horosa-heluo-yaoci-detail">（空爻·无条文）</div>;
		return (
			<div className="horosa-heluo-yaoci">
				<div className="horosa-heluo-yaoci-head">{guaName2} · {yaoName(lines, pos)} <span className="horosa-heluo-verdict">{yt.verdict}</span>{rels.length ? <span className="horosa-heluo-yaoci-rel"> · {rels.join('，')}</span> : null}</div>
				{yt.detail ? <div className="horosa-heluo-yaoci-detail"><b>摘要</b>{yt.detail}</div> : null}
				{yt.shige ? <div className="horosa-heluo-yaoci-shige"><b>诗歌</b>{yt.shige}</div> : null}
				{ni ? <div className="horosa-heluo-yaoci-simple"><b>倪海厦·易经推命</b>{ni}</div> : null}
			</div>
		);
	}

	// 下钻箭头单元格（点击=展开下级；阻止冒泡以免触发本行爻辞）
	arrowCell(onDrill, active) {
		return (
			<td className="horosa-heluo-arrowcell" onClick={(e) => { e.stopPropagation(); onDrill(); }}>
				<span className={`horosa-heluo-arrow${active ? ' is-open' : ''}`}>▾</span>
			</td>
		);
	}

	renderDaxian(m) {
		const segs = m.dy.all;
		return (
			<div className="horosa-huangji-info-card">
				<div className="horosa-huangji-info-heading">大限（歲運）· 阳爻9年/阴爻6年 · 点行看爻辞、点▾看流年</div>
				<table className="horosa-heluo-table horosa-heluo-daxian">
					<thead><tr><th>年龄</th><th>卦</th><th>动爻</th><th>阴阳·吉凶</th><th /></tr></thead>
					<tbody>
						{segs.map((s) => {
							const key = `${s.gua}|${s.pos}|${s.ageStart}`;
							const yt = yaoText(s.gua, s.pos) || {};
							const slot = m.dy.xian.indexOf(s) >= 0 ? 'xiantian' : 'houtian';
							const open = this.state.openYao === `dx:${key}`;
							const drilled = this.state.daxianKey === key;
							return [
								<tr key={key} className={`${drilled ? 'is-active' : ''}${open ? ' is-open' : ''}`} onClick={() => this.setState({ openYao: open ? '' : `dx:${key}` })}>
									<td>{s.ageStart}-{s.ageEnd}</td>
									<td>{s.gua}</td>
									<td>{yaoName(s.lines, s.pos)}</td>
									<td>{s.yang ? '阳9' : '阴6'} {yt.verdict || ''}</td>
									{this.arrowCell(() => this.setState({ daxianKey: drilled ? '' : key, liunianKey: '', liuyueKey: '' }), drilled)}
								</tr>,
								open ? <tr key={`${key}_d`} className="horosa-heluo-detailrow"><td colSpan={5}>{this.renderYaoci(s.gua, s.pos, s.lines, slot, m.chart)}</td></tr> : null,
							];
						})}
					</tbody>
				</table>
				{this.renderLiuNian(m)}
			</div>
		);
	}

	// 流年（点大限▾后出）：列 岁|干支|卦|动爻|理数|▾
	renderLiuNian(m) {
		const segs = m.dy.all;
		const cur = segs.find((s) => `${s.gua}|${s.pos}|${s.ageStart}` === this.state.daxianKey);
		if (!cur) return null;
		const years = liuNian(cur, m.birthYear);
		return (
			<div className="horosa-heluo-drill">
				<div className="horosa-heluo-block-subtitle">流年（{cur.ageStart}-{cur.ageEnd}岁 · {cur.gua}）· 点行看爻辞、点▾看流月</div>
				<table className="horosa-heluo-table">
					<thead><tr><th>岁</th><th>干支</th><th>值年卦</th><th>动爻</th><th>理数</th><th /></tr></thead>
					<tbody>
						{years.map((y) => {
							const lkey = `${cur.ageStart}:${y.age}`;
							const open = this.state.openYao === `ln:${lkey}`;
							const drilled = this.state.liunianKey === lkey;
							return [
								<tr key={y.age} className={`${drilled ? 'is-active' : ''}${open ? ' is-open' : ''}`} onClick={() => this.setState({ openYao: open ? '' : `ln:${lkey}` })}>
									<td>{y.age}</td>
									<td>{y.ganzhi}</td>
									<td>{y.gua}</td>
									<td>{yaoName(y.lines, y.pos)}</td>
									<td className="horosa-heluo-tagcell">{this.liShuCell(y.lines, m.jg, m.chart)}</td>
									{this.arrowCell(() => this.setState({ liunianKey: drilled ? '' : lkey, liuyueKey: '', yearForMonth: y }), drilled)}
								</tr>,
								open ? <tr key={`${y.age}_d`} className="horosa-heluo-detailrow"><td colSpan={6}>{this.renderYaoci(y.gua, y.pos, y.lines, 'liunian', m.chart)}</td></tr> : null,
							];
						})}
					</tbody>
				</table>
				{this.renderLiuYue(m)}
			</div>
		);
	}

	// 流月（点流年▾后出）：列 月|卦|动爻|理数|▾
	renderLiuYue(m) {
		const y = this.state.yearForMonth;
		if (!this.state.liunianKey || !y) return null;
		const months = liuYue(y.lines, y.pos);
		return (
			<div className="horosa-heluo-drill">
				<div className="horosa-heluo-block-subtitle">流月（{y.age}岁 {y.ganzhi}年 · {y.gua}）· 点行看爻辞、点▾看流日</div>
				<table className="horosa-heluo-table">
					<thead><tr><th>月</th><th>流月卦</th><th>动爻</th><th>理数</th><th /></tr></thead>
					<tbody>
						{months.map((mo) => {
							const mkey = `${y.age}:${mo.month}`;
							const open = this.state.openYao === `ly:${mkey}`;
							const drilled = this.state.liuyueKey === mkey;
							return [
								<tr key={mo.month} className={`${drilled ? 'is-active' : ''}${open ? ' is-open' : ''}`} onClick={() => this.setState({ openYao: open ? '' : `ly:${mkey}` })}>
									<td>{mo.label}月</td>
									<td>{mo.gua}</td>
									<td>{yaoName(mo.lines, mo.pos)}</td>
									<td className="horosa-heluo-tagcell">{this.liShuCell(mo.lines, m.jg, m.chart)}</td>
									{this.arrowCell(() => this.setState({ liuyueKey: drilled ? '' : mkey, monthForDay: mo }), drilled)}
								</tr>,
								open ? <tr key={`${mo.month}_d`} className="horosa-heluo-detailrow"><td colSpan={5}>{this.renderYaoci(mo.gua, mo.pos, mo.lines, 'liunian', m.chart)}</td></tr> : null,
							];
						})}
					</tbody>
				</table>
				{this.renderLiuRi(m)}
			</div>
		);
	}

	// 流日（点流月▾后出）：5 卦×6日=30日，动爻自初行至上；列 日|卦|动爻|理数
	renderLiuRi(m) {
		const mo = this.state.monthForDay;
		if (!this.state.liuyueKey || !mo) return null;
		const days = liuRi(mo.lines, mo.pos);
		return (
			<div className="horosa-heluo-drill">
				<div className="horosa-heluo-block-subtitle">流日（{mo.label}月 · {mo.gua}）· 月卦元堂不动、每卦管6日、动爻逐日初→上</div>
				<table className="horosa-heluo-table">
					<thead><tr><th>日</th><th>流日卦</th><th>动爻</th><th>理数</th></tr></thead>
					<tbody>
						{days.map((d) => {
							const dkey = `lr:${mo.month}:${d.dayInMonth}`;
							const open = this.state.openYao === dkey;
							return [
								<tr key={d.dayInMonth} className={open ? 'is-open' : ''} onClick={() => this.setState({ openYao: open ? '' : dkey })}>
									<td>第{d.dayInMonth}日</td>
									<td>{d.gua}</td>
									<td>{yaoName(d.lines, d.pos)}</td>
									<td className="horosa-heluo-tagcell">{this.liShuCell(d.lines, m.jg, m.chart)}</td>
								</tr>,
								open ? <tr key={`${d.dayInMonth}_d`} className="horosa-heluo-detailrow"><td colSpan={4}>{this.renderYaoci(d.gua, d.pos, d.lines, 'liunian', m.chart)}</td></tr> : null,
							];
						})}
					</tbody>
				</table>
			</div>
		);
	}

	renderCenter(m) {
		const { chart, jg, extras } = m;
		const rows = [
			['簡斷', extras.jianDuan],
			['數理', `天數 ${chart.tian}·${extras.shuLi.tian}　地數 ${chart.di}·${extras.shuLi.di}`],
			['氣運', extras.sanhou || '—'],
			['值月消息卦', extras.xiaoxi.gua ? `${extras.xiaoxi.monthLabel}月建${m.monthZhi}·${extras.xiaoxi.gua}` : '—'],
			['元氣化工', `天元 ${jg.yuan.tian.gua}・地元 ${jg.yuan.di.gua}・化工 ${(jg.huagong.guas || []).join('/') || '—'}`],
			['先後天八卦變化', extras.bianYi],
			['五命', `${m.fourPillars.year}生人・${m.nayin || ''}${extras.benWei.length ? `（${extras.benWei.join('、')}）` : ''}`],
		];
		return (
			<div className="horosa-heluo-center">
				<div className="horosa-heluo-toolbar">
					<span className="horosa-heluo-part">{chart.xian.name} → {chart.hou.name}</span>
					<span className="horosa-heluo-sub">天数 {chart.tian}（{chart.tianGua}）· 地数 {chart.di}（{chart.diGua}）· {m.gender}命</span>
				</div>
				<div className="horosa-huangji-info-card">
					<div className="horosa-huangji-info-heading">起卦详情</div>
					{rows.map((r, i) => (
						<div className="horosa-huangji-info-row" key={i}><span>{r[0]}</span><strong>{r[1]}</strong></div>
					))}
				</div>
				{this.renderGuaCard('先天卦（本命·主前段）', chart.xian, jg, this.najia(chart.xian.name), 'xiantian')}
				{this.renderGuaCard('后天卦（主后段）', chart.hou, jg, this.najia(chart.hou.name), 'houtian')}
				{this.renderDaxian(m)}
			</div>
		);
	}

	renderAux(m) {
		const { chart, jg, fourPillars, st } = m;
		const yn = (g) => `${g.name}（${yaoName(g.lines, g.yuan)}）`;
		const yq = (o) => `${o.gua}${o.present ? '（命卦藏·应）' : '（命卦无）'}`;
		const card = (title, rows) => (
			<div className="horosa-huangji-info-card" key={title}>
				<div className="horosa-huangji-info-heading">{title}</div>
				{rows.map((r, i) => (
					<div className="horosa-huangji-info-row" key={i}><span>{r[0]}</span><strong>{r[1]}</strong></div>
				))}
			</div>
		);
		return (
			<Tabs activeKey="pan" tabPosition="top" className="horosa-huangji-tabs horosa-kinastro-tabs">
				<TabPane tab="命盘" key="pan">
					<div className="horosa-heluo-aux horosa-huangji-section-list">
						{card('四柱', [['年柱', fourPillars.year], ['月柱', fourPillars.month], ['日柱', fourPillars.day], ['时柱', fourPillars.hour]])}
						{card('起卦', [
							['天数', `${chart.tian} → ${chart.tianGua}`], ['地数', `${chart.di} → ${chart.diGua}`],
							['先天卦', yn(chart.xian)], ['后天卦', yn(chart.hou)],
							['节气', st && st.term ? `${st.houLabel || st.term}${st.tuyong ? ' · 土用' : ''}` : '—'],
						])}
						{card('卦气', [
							['天元气', yq(jg.yuan.tian)], ['地元气', yq(jg.yuan.di)],
							['反天元', yq(jg.fanYuan.tian)], ['反地元', yq(jg.fanYuan.di)],
							['化工', `${jg.huagong.guas.join('/') || '—'}${jg.huagong.present.length ? `（藏${jg.huagong.present.join('')}）` : ''}`],
							['反化工', `${jg.fanhua.guas.join('/') || '—'}${jg.fanhua.present.length ? `（藏${jg.fanhua.present.join('')}）` : ''}`],
						])}
						{card('得失·二数·元堂', [
							['得势', jg.deSheng ? '✓ 纳甲相逢' : '—'], ['得时', jg.deTime ? '✓ 卦月相逢' : '—'], ['得体', yq(jg.deTi)],
							['二数', `天${jg.erShu.tian}·${jg.erShu.tianState}／地${jg.erShu.di}·${jg.erShu.diState}`],
							['元堂', `${jg.yuanTang.dangWei ? '当位' : '不当位'}·${jg.yuanTang.youYing ? '有应' : '无应'}·${jg.yuanTang.heLi ? '顺气' : '逆气'}`],
							['判格', jg.xie ? '葉（藏元气/化工）' : '不葉'],
						])}
					</div>
				</TabPane>
			</Tabs>
		);
	}

	render() {
		const m = this.getModel();
		if (!m) {
			if (this.props.slot === 'aux') return null;
			return <div style={{ padding: 24 }}><Empty description="请先在左侧输入出生时间" /></div>;
		}
		return this.props.slot === 'aux' ? this.renderAux(m) : this.renderCenter(m);
	}
}

export default HeLuoMain;
