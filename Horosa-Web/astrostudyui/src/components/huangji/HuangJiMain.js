import { Component } from 'react';
import { InputNumber, Spin } from 'antd';
import DateTime from '../comp/DateTime';
import SpaceTimePanel, { buildDateTimeFromFields, formatSpaceTime } from '../comp/SpaceTimePanel';
import XQIcon from '../xq-icons';
import { XQButton as Button, XQSelect as Select, XQTabs as Tabs } from '../xq-ui';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import { ServerRoot, ResultKey } from '../../utils/constants';
import { buildKentangEndpoint } from '../../integrations/kentang/serviceRoot';
import { openKentangCaseDrawer, getKentangSavedCasePayload } from '../../utils/kentangCaseSave';
import { formatHumanValue } from '../../utils/humanReadableFields';
import { defaultAfter23NewDay, defaultLateZiHourUseNextDay } from '../../utils/dayBoundary';

const { Option } = Select;
const { TabPane } = Tabs;

const METHOD_OPTIONS = [
	{ value: 'number', label: '先天数起卦' },
	{ value: 'datetime', label: '年月日時起卦' },
	{ value: 'direction', label: '后天方位起卦' },
	{ value: 'character', label: '字数起卦' },
];

const DEFAULT_CLASSIC = 'huangji_jingshi_shu';

function parseFieldsDateTime(fields){
	if(!fields || !fields.date || !fields.time || !fields.date.value || !fields.time.value){
		return null;
	}
	const dateStr = fields.date.value.format('YYYY-MM-DD');
	const timeStr = fields.time.value.format('HH:mm:ss');
	const d = dateStr.split('-').map((item)=>parseInt(item, 10));
	const t = timeStr.split(':').map((item)=>parseInt(item, 10));
	if(d.length < 3 || t.length < 2){
		return null;
	}
	return {
		year: d[0],
		month: d[1],
		day: d[2],
		hour: t[0],
		minute: t[1],
		second: t[2] || 0,
		date: dateStr,
		time: timeStr,
		zone: fields.zone && fields.zone.value ? fields.zone.value : '',
		after23NewDay: defaultAfter23NewDay(),
		lateZiHourUseNextDay: defaultLateZiHourUseNextDay(),
	};
}

async function postWangJi(path, payload){
	let rsp = null;
	try{
		const rawResponse = await fetch(buildKentangEndpoint('wangji', path), {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json; charset=UTF-8',
			},
			body: JSON.stringify(payload),
		});
		const rawText = await rawResponse.text();
		rsp = rawText ? JSON.parse(rawText) : null;
		if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
			throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'wangji.local.fetch.failed');
		}
	}catch(e){
		const rawResponse = await fetch(`${ServerRoot}/wangji/${path}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json; charset=UTF-8',
			},
			body: JSON.stringify(payload),
		});
		const rawText = await rawResponse.text();
		rsp = rawText ? JSON.parse(rawText) : null;
	}
	if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
		throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'wangji.fetch.failed');
	}
	return rsp && rsp[ResultKey] ? rsp[ResultKey] : rsp;
}

function fmtValue(value){
	return formatHumanValue(value);
}

function buildSnapshotText(pan, xinyi){
	if(!pan){
		return '暂无皇极经世数据';
	}
	const lines = [];
	(pan.sections || []).forEach((section)=>{
		lines.push(`[${section.title}]`);
		(section.rows || []).forEach((row)=>{
			lines.push(`${row.label}：${fmtValue(row.value)}`);
		});
		lines.push('');
	});
	if(xinyi && xinyi.result){
		lines.push('[心易发微]');
		Object.keys(xinyi.result).forEach((key)=>{
			lines.push(`${key}：${fmtValue(xinyi.result[key])}`);
		});
	}
	return lines.join('\n').trim();
}

// 皇极经世 AI 快照(无头):按出生 fields 经 ken 后端起元会运世盘(默认皇极经世书)→ buildSnapshotText。
// aiAnalysisContext 复算用;心易发微(xinyi)属占断叠加,挂载默认不带(传 null);无 pan 即返 ''。
export async function buildHuangJiSnapshotForFields(fields){
	try{
		const dt = parseFieldsDateTime(fields);
		if(!dt){
			return '';
		}
		const pan = await postWangJi('pan', {
			...dt,
			historyYear: dt.year,
			classicKey: DEFAULT_CLASSIC,
		});
		if(!pan){
			return '';
		}
		return buildSnapshotText(pan, null) || '';
	}catch(e){
		return '';
	}
}

class HuangJiMain extends Component{
	constructor(props){
		super(props);
		const dt = buildDateTimeFromFields(props.fields);
		this.state = {
			loading: false,
			pan: null,
			xinyi: null,
			rightPanelTab: 'overview',
			historyYear: dt.year * dt.ad,
			classicKey: DEFAULT_CLASSIC,
			classicSectionIndex: 0,
			classicView: 'section',
			xinyiOptions: {
				method: 'datetime',
				upperNum: 5,
				lowerNum: 10,
				upperStrokes: 5,
				lowerStrokes: 8,
				objectGua: '離',
				direction: '南',
			},
		};
		this.unmounted = false;
		this.timeHook = {};
		this.requestSeq = 0;
		this.onTimeChanged = this.onTimeChanged.bind(this);
		this.getTimeFieldsFromSelector = this.getTimeFieldsFromSelector.bind(this);
		this.clickPlot = this.clickPlot.bind(this);
		this.fetchPan = this.fetchPan.bind(this);
		this.fetchXinyi = this.fetchXinyi.bind(this);
		this.clickSaveCase = this.clickSaveCase.bind(this);
		this.restoreFromCurrentCase = this.restoreFromCurrentCase.bind(this);
		this.setRightPanelTab = this.setRightPanelTab.bind(this);
		this.changeHistoryYear = this.changeHistoryYear.bind(this);
		this.changeClassic = this.changeClassic.bind(this);
		this.changeClassicSection = this.changeClassicSection.bind(this);
		this.changeClassicView = this.changeClassicView.bind(this);
		this.changeXinyiOption = this.changeXinyiOption.bind(this);
		this.randomHistoryYear = this.randomHistoryYear.bind(this);
		this.renderBottomQuickDock = this.renderBottomQuickDock.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields)=>{
				if(this.unmounted){
					return;
				}
				if(!this.restoreFromCurrentCase()){
					this.fetchPan(fields || this.props.fields);
				}
			};
		}
	}

	componentDidMount(){
		this.unmounted = false;
		if(!this.restoreFromCurrentCase(true)){
			this.fetchPan(this.props.fields);
		}
	}

	componentDidUpdate(prevProps){
		if(prevProps.fields !== this.props.fields && this.props.fields){
			if(!this.restoreFromCurrentCase()){
				this.fetchPan(this.props.fields);
			}
		}
	}

	componentWillUnmount(){
		this.unmounted = true;
	}

	restoreFromCurrentCase(force){
		const saved = getKentangSavedCasePayload('huangji');
		if(!saved || !saved.payload){
			return false;
		}
		if(!force && this.lastRestoredCaseId === saved.caseVersion){
			return false;
		}
		const payload = saved.payload;
		const options = payload.options && typeof payload.options === 'object' ? payload.options : {};
		const xinyiOptions = options.xinyiOptions && typeof options.xinyiOptions === 'object'
			? { ...this.state.xinyiOptions, ...options.xinyiOptions }
			: this.state.xinyiOptions;
		this.lastRestoredCaseId = saved.caseVersion;
		this.requestSeq += 1;
		this.setState({
			loading: false,
			pan: payload.pan || null,
			xinyi: payload.xinyi || null,
			historyYear: options.historyYear !== undefined ? options.historyYear : this.state.historyYear,
			classicKey: options.classicKey || this.state.classicKey,
			classicSectionIndex: options.classicSectionIndex !== undefined ? options.classicSectionIndex : this.state.classicSectionIndex,
			classicView: options.classicView || this.state.classicView,
			xinyiOptions,
		}, ()=>{
			saveModuleAISnapshot('huangji', buildSnapshotText(this.state.pan, this.state.xinyi));
		});
		return true;
	}

	onFieldsChange(field){
		if(this.props.dispatch){
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

	onTimeChanged(value){
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
		this.fetchPan(nextFields);
	}

	async fetchPan(fields){
		const dt = parseFieldsDateTime(fields);
		if(!dt){
			return;
		}
		const reqSeq = ++this.requestSeq;
		this.setState({ loading: true });
		try{
			const pan = await postWangJi('pan', {
				...dt,
				historyYear: this.state.historyYear,
				classicKey: this.state.classicKey,
			});
			const xinyi = await this.fetchXinyi(fields, false);
			if(this.unmounted || reqSeq !== this.requestSeq){
				return;
			}
			this.setState({ pan, xinyi, loading: false }, ()=>{
				saveModuleAISnapshot('huangji', buildSnapshotText(pan, xinyi));
			});
		}catch(e){
			console.warn('kinwangji backend failed', e);
			if(!this.unmounted && reqSeq === this.requestSeq){
				this.setState({ loading: false });
			}
		}
	}

	async fetchXinyi(fields, updateState = true){
		const dt = parseFieldsDateTime(fields || this.props.fields) || {};
		const opt = this.state.xinyiOptions;
		const payload = {
			...dt,
			method: opt.method,
			upperNum: opt.upperNum,
			lowerNum: opt.lowerNum,
			upperStrokes: opt.upperStrokes,
			lowerStrokes: opt.lowerStrokes,
			objectGua: opt.objectGua,
			direction: opt.direction,
		};
		const xinyi = await postWangJi('xinyi', payload);
		if(updateState && !this.unmounted){
			this.setState({ xinyi }, ()=>{
				saveModuleAISnapshot('huangji', buildSnapshotText(this.state.pan, xinyi));
			});
		}
		return xinyi;
	}

	clickSaveCase(){
		openKentangCaseDrawer({
			dispatch: this.props.dispatch,
			fields: this.props.fields,
			module: 'huangji',
			label: '皇极经世',
			payload: {
				options: {
					historyYear: this.state.historyYear,
					classicKey: this.state.classicKey,
					classicSectionIndex: this.state.classicSectionIndex,
					classicView: this.state.classicView,
					xinyiOptions: this.state.xinyiOptions,
				},
				pan: this.state.pan,
				xinyi: this.state.xinyi,
				snapshot: buildSnapshotText(this.state.pan, this.state.xinyi),
			},
		});
	}

	setRightPanelTab(key){
		this.setState({ rightPanelTab: key });
	}

	changeHistoryYear(value){
		const historyYear = value || new Date().getFullYear();
		this.setState({ historyYear }, ()=>this.fetchPan(this.props.fields));
	}

	changeClassic(value){
		this.setState({
			classicKey: value || DEFAULT_CLASSIC,
			classicSectionIndex: 0,
		}, ()=>this.fetchPan(this.props.fields));
	}

	changeClassicSection(value){
		const idx = parseInt(value, 10);
		this.setState({ classicSectionIndex: Number.isFinite(idx) ? idx : 0 });
	}

	changeClassicView(value){
		this.setState({ classicView: value || 'section' });
	}

	randomHistoryYear(){
		const historyYear = 1900 + Math.floor(Math.random() * 201);
		this.setState({ historyYear }, ()=>this.fetchPan(this.props.fields));
	}

	changeXinyiOption(key, value){
		const xinyiOptions = {
			...this.state.xinyiOptions,
			[key]: value,
		};
		this.setState({ xinyiOptions });
	}

	renderInputPanel(){
		const fields = this.props.fields || {};
		const datetm = buildDateTimeFromFields(fields);
		const pan = this.state.pan;
		const classics = pan && pan.classics && pan.classics.meta ? pan.classics.meta : [];
		const classicSections = pan && pan.classics && pan.classics.sections ? pan.classics.sections : [];
		const xOpt = this.state.xinyiOptions;
		const trigrams = pan && pan.xinyiOptions ? (pan.xinyiOptions.trigrams || []) : ['乾', '兌', '離', '震', '巽', '坎', '艮', '坤'];
		const directions = pan && pan.xinyiOptions ? (pan.xinyiOptions.directions || []) : ['北', '東北', '東', '東南', '南', '西南', '西', '西北', '中'];
		return (
			<div className="horosa-huangji-input-stack">
				<div>
					<div className="horosa-side-panel-title">皇极经世设置</div>
					<div className="horosa-side-panel-subtitle">时间、心易与起盘选项</div>
				</div>
				<SpaceTimePanel
					fields={fields}
					value={datetm}
					timeText={formatSpaceTime(fields, '---- -- -- --:--:--')}
					onTimeChange={this.onTimeChanged}
					timeHook={this.timeHook}
					showLocation={false}
				/>
				<div className="horosa-huangji-input-section">
					<div className="horosa-huangji-field-title"><XQIcon name="other" />皇极选项</div>
					<div className="horosa-huangji-select-grid">
						<label className="horosa-huangji-select-field">
							<span>历史年</span>
							<InputNumber value={this.state.historyYear} onChange={this.changeHistoryYear} min={-4712} max={9999} />
						</label>
						<label className="horosa-huangji-select-field">
							<span>经典</span>
							<Select value={this.state.classicKey} onChange={this.changeClassic}>
								{classics.map((item)=><Option key={item.key} value={item.key}>{item.title}</Option>)}
								{classics.length === 0 ? <Option value={DEFAULT_CLASSIC}>皇极经世书</Option> : null}
							</Select>
						</label>
						<label className="horosa-huangji-select-field is-wide">
							<span>典籍章节</span>
							<Select value={`${this.state.classicSectionIndex}`} onChange={this.changeClassicSection}>
								{classicSections.length === 0 ? <Option value="0">暂无章节</Option> : null}
								{classicSections.map((item, idx)=><Option key={`${item.title}_${idx}`} value={`${idx}`}>{item.title}</Option>)}
							</Select>
						</label>
						<label className="horosa-huangji-select-field">
							<span>典籍显示</span>
							<Select value={this.state.classicView} onChange={this.changeClassicView}>
								<Option value="section">选中章节</Option>
								<Option value="catalog">章节目录</Option>
							</Select>
						</label>
						<label className="horosa-huangji-select-field">
							<span>历史抽取</span>
							<Button onClick={this.randomHistoryYear}>随机历史年</Button>
						</label>
					</div>
				</div>
				<div className="horosa-huangji-input-section">
					<div className="horosa-huangji-field-title"><XQIcon name="quickComposite" />心易发微</div>
					<div className="horosa-huangji-select-grid">
						<label className="horosa-huangji-select-field is-wide">
							<span>起卦法</span>
							<Select value={xOpt.method} onChange={(v)=>this.changeXinyiOption('method', v)}>
								{METHOD_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						{xOpt.method === 'number' ? (
							<>
								<label className="horosa-huangji-select-field">
									<span>上卦数</span>
									<InputNumber value={xOpt.upperNum} min={1} onChange={(v)=>this.changeXinyiOption('upperNum', v || 1)} />
								</label>
								<label className="horosa-huangji-select-field">
									<span>下卦数</span>
									<InputNumber value={xOpt.lowerNum} min={1} onChange={(v)=>this.changeXinyiOption('lowerNum', v || 1)} />
								</label>
							</>
						) : null}
						{xOpt.method === 'direction' ? (
							<>
								<label className="horosa-huangji-select-field">
									<span>物象</span>
									<Select value={xOpt.objectGua} onChange={(v)=>this.changeXinyiOption('objectGua', v)}>
										{trigrams.map((item)=><Option key={item} value={item}>{item}</Option>)}
									</Select>
								</label>
								<label className="horosa-huangji-select-field">
									<span>方位</span>
									<Select value={xOpt.direction} onChange={(v)=>this.changeXinyiOption('direction', v)}>
										{directions.map((item)=><Option key={item} value={item}>{item}</Option>)}
									</Select>
								</label>
							</>
						) : null}
						{xOpt.method === 'character' ? (
							<>
								<label className="horosa-huangji-select-field">
									<span>上/左笔画</span>
									<InputNumber value={xOpt.upperStrokes} min={1} onChange={(v)=>this.changeXinyiOption('upperStrokes', v || 1)} />
								</label>
								<label className="horosa-huangji-select-field">
									<span>下/右笔画</span>
									<InputNumber value={xOpt.lowerStrokes} min={1} onChange={(v)=>this.changeXinyiOption('lowerStrokes', v || 1)} />
								</label>
							</>
						) : null}
					</div>
				</div>
				<div className="horosa-huangji-action-row">
					<Button type="primary" onClick={this.clickPlot}>起盘</Button>
					<Button onClick={()=>this.fetchXinyi(this.props.fields)}>起心易</Button>
				</div>
			</div>
		);
	}

	renderHexCard(key, label, movingKey){
		const raw = this.state.pan && this.state.pan.raw ? this.state.pan.raw : {};
		const gua = raw[key] || '';
		const symbol = this.state.pan && this.state.pan.guaUnicode ? this.state.pan.guaUnicode[gua] : '';
		const moving = movingKey ? raw[movingKey] : '';
		return (
			<div className="horosa-huangji-gua-card" key={key}>
				<div className="horosa-huangji-gua-symbol">{symbol || '䷀'}</div>
				<strong>{gua || '—'}</strong>
				<span>{label}{moving ? ` · 动爻${moving}` : ''}</span>
			</div>
		);
	}

	renderCenter(){
		const pan = this.state.pan;
		if(!pan){
			return <div className="horosa-huangji-empty">暂无皇极经世数据</div>;
		}
		const raw = pan.raw || {};
		const gz = raw['干支'] || [];
		const gzItems = ['年柱', '月柱', '日柱', '时柱', '分柱'].map((label, idx)=>({
			label,
			value: gz[idx] || raw[label] || '—',
		}));
		const wangxiang = pan.wangxiang && pan.wangxiang[1] ? pan.wangxiang[1] : {};
		const macro = [
			this.renderHexCard('正卦', '正卦'),
			this.renderHexCard('運卦', '运卦', '運卦動爻'),
			this.renderHexCard('世卦', '世卦', '世卦動爻'),
			this.renderHexCard('旬卦', '旬卦', '旬卦動爻'),
		];
		const micro = [
			this.renderHexCard('年卦', '年卦'),
			this.renderHexCard('月卦', '月卦'),
			this.renderHexCard('日卦', '日卦'),
			this.renderHexCard('時卦', '时卦'),
			this.renderHexCard('分卦', '分卦'),
		];
		return (
			<div className="horosa-huangji-board">
				<div className="horosa-huangji-board-header">
					<div>
						<h2>皇极经世</h2>
					</div>
					<div className="horosa-huangji-board-time">{raw['日期'] || '—'}</div>
				</div>
					<div className="horosa-huangji-meta-grid">
						<div><span>节气</span><strong>{pan.solarTerm || '—'}</strong></div>
						<div><span>旺相</span><strong>旺{wangxiang['旺'] || '—'} · 相{wangxiang['相'] || '—'}</strong></div>
						<div><span>农历</span><strong>{pan.lunarDate && pan.lunarDate.text ? pan.lunarDate.text : '—'}</strong></div>
						<div className="horosa-huangji-ganzhi-card">
							<span>干支</span>
						<div className="horosa-huangji-ganzhi-grid">
							{gzItems.map((item)=>(
								<div className="horosa-huangji-ganzhi-item" key={item.label}>
									<em>{item.label}</em>
									<strong>{item.value}</strong>
								</div>
							))}
						</div>
					</div>
				</div>
				<div className="horosa-huangji-cycle-row">
					<div><span>会</span><strong>{raw['會']}</strong><small>一元十二会</small></div>
					<div><span>运</span><strong>{raw['運']}</strong><small>一会三十运</small></div>
					<div><span>世</span><strong>{raw['世']}</strong><small>一运十二世</small></div>
				</div>
				<div className="horosa-huangji-gua-section">
					<div className="horosa-huangji-section-title">天道卦</div>
					<div className="horosa-huangji-gua-grid is-macro">{macro}</div>
				</div>
				<div className="horosa-huangji-gua-section">
					<div className="horosa-huangji-section-title">人事卦</div>
					<div className="horosa-huangji-gua-grid">{micro}</div>
				</div>
			</div>
		);
	}

	renderRows(sections){
		const list = sections || [];
		if(!list.length){
			return <div className="horosa-huangji-empty">暂无数据</div>;
		}
		return list.map((section)=>(
			<div className="horosa-huangji-info-card" key={section.title}>
				<div className="horosa-huangji-info-heading">{section.title}</div>
				{(section.rows || []).map((row, idx)=>(
					<div className="horosa-huangji-info-row" key={`${section.title}_${row.label}_${idx}`}>
						<span>{row.label}</span>
						<strong>{fmtValue(row.value)}</strong>
					</div>
				))}
			</div>
		));
	}

	renderXinyi(){
		const xinyi = this.state.xinyi || (this.state.pan && this.state.pan.xinyi);
		if(!xinyi || !xinyi.result){
			return <div className="horosa-huangji-empty">暂无心易发微数据</div>;
		}
		const result = xinyi.result;
		return (
			<div className="horosa-huangji-xinyi">
				<div className="horosa-huangji-gua-grid is-xinyi">
					{['本卦', '變卦', '互卦'].map((key)=>(
						<div className="horosa-huangji-gua-card" key={key}>
							<div className="horosa-huangji-gua-symbol">{this.state.pan && this.state.pan.guaUnicode ? this.state.pan.guaUnicode[result[key]] : '䷀'}</div>
							<strong>{fmtValue(result[key])}</strong>
							<span>{key.replace('變', '变')}</span>
						</div>
					))}
				</div>
				{this.renderRows(xinyi.sections || [{ title: '心易发微', rows: Object.keys(result).map((key)=>({ label: key, value: result[key] })) }])}
			</div>
		);
	}

	renderHistory(){
		const records = this.state.pan && this.state.pan.history ? this.state.pan.history : [];
		if(!records.length){
			return <div className="horosa-huangji-empty">暂无历史年表</div>;
		}
		return this.renderRows([{
			title: `${this.state.historyYear}年历史对照`,
			rows: records.reduce((rows, rec, idx)=>{
				rows.push({ label: `记录${idx + 1}`, value: `${fmtValue(rec.dynasty)} ${fmtValue(rec.title)} ${fmtValue(rec.name)} ${fmtValue(rec.era)}` });
				rows.push({ label: '范围', value: `${rec.start_year}起，${rec.duration}年` });
				return rows;
			}, []),
		}]);
	}

	renderClassics(){
		const classics = this.state.pan && this.state.pan.classics ? this.state.pan.classics : null;
		if(!classics || !classics.sections || !classics.sections.length){
			return <div className="horosa-huangji-empty">暂无经典文本</div>;
		}
		const meta = (classics.meta || []).find((item)=>item.key === classics.selectedKey);
		const idx = Math.max(0, Math.min(this.state.classicSectionIndex || 0, classics.sections.length - 1));
		const selectedSection = classics.sections[idx];
		const displaySections = this.state.classicView === 'catalog'
			? classics.sections
			: (selectedSection ? [selectedSection] : []);
		return (
			<div className="horosa-huangji-classics">
				{meta ? (
					<div className="horosa-huangji-info-card">
						<div className="horosa-huangji-info-heading">{meta.title}</div>
						<div className="horosa-huangji-info-row"><span>作者</span><strong>{meta.author}</strong></div>
						<div className="horosa-huangji-info-row"><span>说明</span><strong>{meta.description}</strong></div>
					</div>
				) : null}
				<div className="horosa-huangji-classic-list">
					{displaySections.map((section, sectionIdx)=>(
						<div className="horosa-huangji-classic-section" key={`${section.title}_${sectionIdx}`}>
							<strong>{section.title}</strong>
							<p>{this.state.classicView === 'catalog' ? (section.content || '本节无正文内容').slice(0, 420) : (section.content || '本节无正文内容')}</p>
							{this.state.classicView === 'catalog' && section.content && section.content.length > 420 ? <em>已显示摘要，可在左侧选择本章查看全文。</em> : null}
						</div>
					))}
				</div>
			</div>
		);
	}

	renderRightPanel(){
		const pan = this.state.pan;
		const activeKey = ['overview', 'gua', 'xinyi', 'history'].indexOf(this.state.rightPanelTab) >= 0 ? this.state.rightPanelTab : 'overview';
		return (
			<Tabs activeKey={activeKey} onChange={this.setRightPanelTab} defaultActiveKey="overview" tabPosition="top" className="horosa-huangji-tabs">
				<TabPane tab="概览" key="overview">
					<div className="horosa-huangji-section-list">
						{this.renderRows(pan ? (pan.sections || []).slice(0, 2) : [])}
					</div>
				</TabPane>
				<TabPane tab="卦象" key="gua">
					<div className="horosa-huangji-section-list">
						{this.renderRows(pan ? (pan.sections || []).slice(2, 4) : [])}
					</div>
				</TabPane>
				<TabPane tab="心易" key="xinyi">
					<div className="horosa-huangji-section-list">{this.renderXinyi()}</div>
				</TabPane>
				<TabPane tab="年表" key="history">
					<div className="horosa-huangji-section-list">{this.renderHistory()}</div>
				</TabPane>
			</Tabs>
		);
	}

	renderBottomQuickDock(){
		const actions = [
			{ label: '起盘', icon: 'quickPrimary', onClick: this.clickPlot },
			{ label: '概览', icon: 'quickComposite', active: this.state.rightPanelTab === 'overview', onClick: ()=>this.setRightPanelTab('overview') },
			{ label: '卦象', icon: 'quickTransit', active: this.state.rightPanelTab === 'gua', onClick: ()=>this.setRightPanelTab('gua') },
			{ label: '心易', icon: 'quickFirdaria', active: this.state.rightPanelTab === 'xinyi', onClick: ()=>this.setRightPanelTab('xinyi') },
			{ label: '年表', icon: 'quickNote', active: this.state.rightPanelTab === 'history', onClick: ()=>this.setRightPanelTab('history') },
			{ label: '保存', icon: 'quickReturn', onClick: this.clickSaveCase },
		];
		return (
			<div className="horosa-bottom-quick-dock horosa-huangji-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-huangji-quick-actions">
					{actions.map((item)=>(
						<button
							type="button"
							key={item.label}
							className={`horosa-bottom-quick-button horosa-huangji-quick-button${item.active ? ' is-active' : ''}`}
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

	render(){
		const embedded = !!this.props.hideQuickDock;
		let height = this.props.height ? this.props.height : 760;
		let pageStyle = { height, minHeight: height, overflow: 'hidden' };
		if(embedded){
			pageStyle = { height: '100%', minHeight: 0, overflow: 'hidden' };
		}else if(height === '100%'){
			height = 760;
			pageStyle = { height, minHeight: height, overflow: 'hidden' };
		}else{
			height = height - 20;
			pageStyle = { height, minHeight: height, overflow: 'hidden' };
		}
		return (
			<div className={`horosa-huangji-page horosa-astro-redesign horosa-huangji-redesign${embedded ? ' horosa-huangji-embedded' : ''}`} style={pageStyle}>
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-huangji-redesign-layout">
					<Spin spinning={this.state.loading}>
						<div className="horosa-astro-redesign-grid horosa-huangji-redesign-grid">
							<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-huangji-input-panel">
								{this.renderInputPanel()}
							</div>
							<div className="horosa-chart-stage horosa-chart-stage-redesign horosa-huangji-chart-panel xq-chart-renderer">
								<div className="horosa-huangji-board-host">{this.renderCenter()}</div>
							</div>
							<div className="horosa-inspector-panel horosa-astro-content-panel horosa-huangji-info-panel">
								<div className="horosa-side-panel-heading horosa-huangji-info-heading-main">
									<div>
										<div className="horosa-side-panel-title">皇极信息</div>
										<div className="horosa-side-panel-subtitle">卦象、心易与年表</div>
									</div>
								</div>
								{this.renderRightPanel()}
							</div>
						</div>
					</Spin>
					{!this.props.hideQuickDock && this.renderBottomQuickDock()}
				</div>
			</div>
		);
	}
}

export default HuangJiMain;
